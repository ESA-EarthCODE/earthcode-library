"""
Load documents from the specified STAC open science catalog and upload to s3 storage as lance table.

Currently only handles OSC collections/catalogs for 'products', 'variables', 'eo-missions', and 'projects'.
It does NOT handle the stac items within collections. In future this can be handled with multiple indexes and tables.

- Build (defaults baked in): `pixi run python generate_embeddings.py`
- Explicit build: `pixi run python generate_embeddings.py --products-dir open-science-catalog-metadata/products --lance-uri s3://pangeo-test-fires/vector_store_v3/ --browser-out-dir vector_store_browser_v2 --model BAAI/bge-small-en-v1.5`


Returns:
    None
"""

import argparse
import json
from pathlib import Path
import lance
import numpy as np
import pyarrow as pa
from fastembed import TextEmbedding

DEFAULT_ROOT_DIR = "../open-science-catalog-metadata"
DEFAULT_GROUPS = ["products", "variables", "eo-missions", "projects"]
DEFAULT_LANCE_URI = "s3://pangeo-test-fires/vector_store_v5/"
LANCE_BASE_STORAGE_OPTIONS = {
    "region": "eu-west-2",
    "aws_skip_signature": "true",
}  # to be implemented
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------- helpers ---------------------------- #


def extract_theme_ids(data):
    theme_ids = []
    for theme in data.get("themes", []):
        for concept in theme.get("concepts", []):
            cid = concept.get("id")
            if cid:
                theme_ids.append(str(cid))
    return theme_ids


def flatten_metadata(data):
    parts = []
    parts.append(data.get("id", ""))
    parts.append(data.get("title", ""))
    parts.append(data.get("description", ""))
    parts.extend(data.get("keywords", []))
    parts.extend(data.get("osc:variables", []))
    parts.extend(data.get("osc:missions", []))
    parts.extend(extract_theme_ids(data))
    return "\n".join(p for p in parts if p)


def create_row_from_stac_file(path, group):
    data = json.loads(path.read_text())
    theme_ids = extract_theme_ids(data)
    variable_ids = [str(v) for v in data.get("osc:variables", []) if v]
    mission_ids = [str(m) for m in data.get("osc:missions", []) if m]
    keywords = [str(k) for k in data.get("keywords", []) if k]
    bboxes = data.get("extent", {}).get("spatial", {}).get("bbox") or [
        [-180, -90, 180, 90]
    ]
    bminx = min([b[0] for b in bboxes if len(b) >= 4], default=None)
    bminy = min([b[1] for b in bboxes if len(b) >= 4], default=None)
    bmaxx = max([b[2] for b in bboxes if len(b) >= 4], default=None)
    bmaxy = max([b[3] for b in bboxes if len(b) >= 4], default=None)
    return {
        "id": data.get("id", path.parent.name),
        "group": group,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "path": str(path),
        "bbox_minx": bminx,
        "bbox_miny": bminy,
        "bbox_maxx": bmaxx,
        "bbox_maxy": bmaxy,
        "item_json": json.dumps(data),
        "theme_ids": f"|{'|'.join(theme_ids)}|" if theme_ids else "",
        "variable_ids": f"|{'|'.join(variable_ids)}|" if variable_ids else "",
        "mission_ids": f"|{'|'.join(mission_ids)}|" if mission_ids else "",
        "keywords": f"|{'|'.join(keywords)}|" if keywords else "",
        "text": flatten_metadata(data),
    }


def load_documents(stac_dir, group):
    if not stac_dir.exists():
        raise FileNotFoundError(f"Group dir not found: {stac_dir}")

    targets = list(stac_dir.glob("**/collection.json")) + list(
        stac_dir.glob("**/catalog.json")
    )
    rows = [create_row_from_stac_file(p, group) for p in sorted(targets)]

    if not rows:
        raise RuntimeError(f"No STAC collections/catalogs found under {stac_dir}")
    return rows


def build_embeddings(texts, model_name):
    model = TextEmbedding(model_name=model_name)
    return np.asarray(list(model.embed(texts)), dtype=np.float32)


# ----------------------------- main ------------------------------ #


def main():
    parser = argparse.ArgumentParser(description="Build Lance dataset.")
    parser.add_argument(
        "--root-dir",
        default=DEFAULT_ROOT_DIR,
        help="Base OSC metadata dir containing group folders.",
    )
    parser.add_argument(
        "--groups",
        nargs="+",
        default=DEFAULT_GROUPS,
        help="Group folder names under root-dir to ingest (e.g., products variables eo-missions projects).",
    )
    parser.add_argument(
        "--lance-uri",
        default=DEFAULT_LANCE_URI,
        help="Where to write the Lance dataset.",
    )
    parser.add_argument(
        "--model", default=MODEL_NAME, help="FastEmbed model name."
    )
    args = parser.parse_args()

    # get documents in pyarrow table
    root = Path(args.root_dir)
    rows = [row for grp in args.groups for row in load_documents(root / grp, grp)]

    # build embeddings
    texts = [r["text"] for r in rows]
    embeddings = build_embeddings(texts, args.model)
    embed_array = pa.FixedSizeListArray.from_arrays(
        pa.array(embeddings.astype(np.float32).ravel(), type=pa.float32()),
        embeddings.shape[1],
    )

    # build and write lance dataset
    table = pa.Table.from_pylist(rows)
    table = table.append_column("embedding", embed_array)
    table = table.drop(["text"])
    lance.write_dataset(table, args.lance_uri, mode="overwrite")

    print(
        f"Wrote {table.num_rows} rows to {args.lance_uri} with dim={embeddings.shape[1]}"
    )


if __name__ == "__main__":
    main()
