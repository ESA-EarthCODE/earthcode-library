"""Search interface for Lance vector store of Open Science Catalog items."""
import json
import os
from pathlib import Path
import shutil

import lance
import numpy as np
import onnxruntime as ort
from platformdirs import user_cache_path
import pystac
import requests
from tokenizers import Tokenizer

LANCE_URI = "s3://pangeo-test-fires/vector_store_v6_local/"
MODEL_SOURCE = "https://pangeo-test-fires.s3.eu-west-2.amazonaws.com/self-hosted-models"
MODEL_FILE = "model_O4.onnx"
TOKENIZER_FILE = "tokenizer.json"
MAX_LENGTH = 256
MODEL_CACHE_DIR = user_cache_path("earthcode") / "model-bundles"
MODEL_DIR_NAME = Path(MODEL_FILE).stem
MODEL_ASSETS = (
    (MODEL_FILE, f"{MODEL_SOURCE}/{MODEL_FILE}"),
    (TOKENIZER_FILE, f"{MODEL_SOURCE}/{TOKENIZER_FILE}"),
)
MODEL_DOWNLOAD_TIMEOUT = 60
LANCE_BASE_STORAGE_OPTIONS = {
    "region": "eu-west-2",
    "aws_skip_signature": "true",
}
OPEN_SCIENCE_CATALOG_LINK = "https://opensciencedata.esa.int/stac-browser/#"
URL_TO_INJECT = {
    "products": OPEN_SCIENCE_CATALOG_LINK + "/products/{id}/collection.json",
    "variables": OPEN_SCIENCE_CATALOG_LINK + "/variables/{id}/catalog.json",
    "projects": OPEN_SCIENCE_CATALOG_LINK + "/projects/{id}/collection.json",
    "eo-missions": OPEN_SCIENCE_CATALOG_LINK + "/eo-missions/{id}/catalog.json",
    "themes": OPEN_SCIENCE_CATALOG_LINK + "/themes/{id}/catalog.json",
    "experiments": OPEN_SCIENCE_CATALOG_LINK + "/experiments/{id}/record.json",
    "workflows": OPEN_SCIENCE_CATALOG_LINK + "/workflows/{id}/record.json",
}

_ds = None
_embedding_runtime = {}


def _get_cached_model_bundle(model_cache_dir=None):
    cache_root = Path(
        os.getenv("EARTHCODE_MODEL_CACHE_DIR") or model_cache_dir or MODEL_CACHE_DIR
    ).expanduser().resolve()
    model_dir = cache_root / MODEL_DIR_NAME
    if all((model_dir / filename).exists() for filename, _ in MODEL_ASSETS):
        return model_dir

    if model_dir.exists():
        shutil.rmtree(model_dir, ignore_errors=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    def download_file(filename, uri):
        cached_path = model_dir / filename
        show_progress = filename == MODEL_FILE
        with requests.get(uri, stream=True, timeout=MODEL_DOWNLOAD_TIMEOUT) as response:
            if response.status_code == 404:
                raise FileNotFoundError(f"File '{filename}' not found in {MODEL_SOURCE}")
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with cached_path.open("wb") as dst:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        dst.write(chunk)
                        downloaded += len(chunk)
                        if show_progress and total:
                            remaining_mb = max(total - downloaded, 0) / (1024 * 1024)
                            print(f"\r Downloading Mini LLM Model: {remaining_mb:.1f} MB left", end="", flush=True)
            if show_progress and total:
                print()

    try:
        for filename, uri in MODEL_ASSETS: # was parallel before
            download_file(filename, uri)
    except Exception:
        shutil.rmtree(model_dir, ignore_errors=True)
        raise

    if not all((model_dir / filename).exists() for filename, _ in MODEL_ASSETS):
        raise FileNotFoundError(f"Model files missing in cache {model_dir}")
    return model_dir


def _load_embedding_runtime(model_cache_dir=None):
    model_dir = _get_cached_model_bundle(model_cache_dir)
    cache_key = str(model_dir)
    if cache_key in _embedding_runtime:
        return _embedding_runtime[cache_key]

    model_path = model_dir / MODEL_FILE
    tokenizer_path = model_dir / TOKENIZER_FILE
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    pad_id = tokenizer.token_to_id("[PAD]") or 0
    tokenizer.enable_truncation(max_length=MAX_LENGTH)
    tokenizer.enable_padding(pad_id=pad_id, pad_token="[PAD]")

    session = ort.InferenceSession(str(model_path))
    runtime = (model_dir, tokenizer, session)
    _embedding_runtime[cache_key] = runtime
    return runtime


def _mean_pool(last_hidden_state, attention_mask):
    mask = attention_mask.astype(np.float32)[..., None]
    summed = (last_hidden_state * mask).sum(axis=1)
    counts = np.clip(mask.sum(axis=1), 1e-12, None)
    return summed / counts


def _l2_normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


def _embed_texts(texts, *, model_cache_dir=None):
    _, tokenizer, session = _load_embedding_runtime(model_cache_dir)

    encodings = tokenizer.encode_batch([text or "" for text in texts])
    input_ids = np.asarray([encoding.ids for encoding in encodings], dtype=np.int64)
    attention_mask = np.asarray(
        [encoding.attention_mask for encoding in encodings], dtype=np.int64
    )
    token_type_ids = np.asarray(
        [encoding.type_ids for encoding in encodings], dtype=np.int64
    )

    ort_inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }
    input_names = {input_def.name for input_def in session.get_inputs()}
    if "token_type_ids" in input_names:
        ort_inputs["token_type_ids"] = token_type_ids

    last_hidden_state = np.asarray(
        session.run(None, ort_inputs)[0], dtype=np.float32
    )
    pooled = _mean_pool(last_hidden_state, attention_mask)
    return _l2_normalize(pooled).astype(np.float32)


def search(
    query=None,
    *,
    limit=10,
    bbox=None,
    intersects=True,
    collection_ids=None,
    theme=None,
    variable=None,
    mission=None,
    keyword=None,
    type="products",
):
    # check valid inputs for type
    if type not in ("products", "variables", "eo-missions", "projects"):
        raise ValueError(
            f"Invalid type '{type}'. Must be one of 'products', 'variables', 'eo-missions', or 'projects'."
        )

    # check valid inputs for themes:
    valid_themes = {
        "land",
        "oceans",
        "atmosphere",
        "cryosphere",
        "magnetosphere-ionosphere",
        "solid-earth",
    }
    if theme:
        themes = (
            theme if isinstance(theme, (list, tuple, set)) else [theme]
        )  # handle if list or str
        for t in themes:
            if t not in valid_themes:
                raise ValueError(
                    f"Invalid theme '{t}'. Must be one of {sorted(valid_themes)}."
                )

    vec = None
    if query and query.strip():
        vec = _embed_texts([query])[0]

    # build filter string
    parts = []
    parts.append(f"`group` = '{type}'")
    if collection_ids:
        if isinstance(collection_ids, str):
            collection_ids = [collection_ids]
        parts.append("id IN (" + ",".join(f"'{c}'" for c in collection_ids) + ")")

    if theme and type in ("products", "variables"):
        themes = (
            theme if isinstance(theme, (list, tuple, set)) else [theme]
        )  # handle if list or str
        theme_filters = [
            f"LOWER(theme_ids) LIKE '%|{str(t).lower()}|%'" for t in themes if t
        ]
        if theme_filters:
            parts.append("(" + " OR ".join(theme_filters) + ")")

    if variable and type == "products":
        variables = variable if isinstance(variable, (list, tuple, set)) else [variable]
        variable_filters = [
            f"LOWER(variable_ids) LIKE '%|{str(v).lower()}|%'" for v in variables if v
        ]
        if variable_filters:
            parts.append("(" + " OR ".join(variable_filters) + ")")

    if mission and type == "products":
        missions = mission if isinstance(mission, (list, tuple, set)) else [mission]
        mission_filters = [
            f"LOWER(mission_ids) LIKE '%|{str(m).lower()}|%'" for m in missions if m
        ]
        if mission_filters:
            parts.append("(" + " OR ".join(mission_filters) + ")")

    if keyword:
        keywords = keyword if isinstance(keyword, (list, tuple, set)) else [keyword]
        kw_filters = [
            "("
            + " OR ".join(
                [
                    f"LOWER(title) LIKE '%{str(kw).lower()}%'",
                    f"LOWER(description) LIKE '%{str(kw).lower()}%'",
                    f"LOWER(keywords) LIKE '%|{str(kw).lower()}|%'",
                ]
            )
            + ")"
            for kw in keywords
            if kw
        ]
        if kw_filters:
            parts.append("(" + " OR ".join(kw_filters) + ")")

    if bbox and len(bbox) >= 4:
        minx, miny, maxx, maxy = bbox[:4]
        if intersects:
            parts.append(
                f"bbox_minx <= {maxx} AND bbox_maxx >= {minx} AND bbox_miny <= {maxy} AND bbox_maxy >= {miny}"
            )
        else:
            parts.append(
                f"bbox_minx >= {minx} AND bbox_maxx <= {maxx} AND bbox_miny >= {miny} AND bbox_maxy <= {maxy}"
            )

    filt = " AND ".join(parts) if parts else None

    cols = [
        "id",
        "group",
        "title",
        "description",
        "keywords",
        "bbox_minx",
        "bbox_miny",
        "bbox_maxx",
        "bbox_maxy",
        "item_json",
    ]

    global _ds
    if _ds is None or getattr(_ds, "uri", None) != LANCE_URI.rstrip("/") + "/":
        _ds = lance.dataset(
            LANCE_URI.rstrip("/") + "/", storage_options=LANCE_BASE_STORAGE_OPTIONS
        )

    if vec is not None:
        tbl = _ds.scanner(
            columns=cols,
            filter=filt,
            nearest={
                "column": "embedding",
                "q": np.asarray(vec, dtype=np.float32),
                "k": limit,
            },
            disable_scoring_autoprojection=True,
            prefilter=True,
            limit=limit,
        ).to_table()

    else:
        tbl = _ds.to_table(columns=cols, filter=filt, limit=limit)

    results = []

    for row in tbl.to_pylist():
        item_j = json.loads(row["item_json"])
        item = (
            pystac.Collection.from_dict(item_j)
            if item_j.get("type") == "Collection"
            else pystac.Catalog.from_dict(item_j)
        )
        item.extra_fields["osc_url"] = URL_TO_INJECT.get(type, "").format(id=row["id"])

        results.append(item)
    return results


# if __name__ == "__main__":
# for grp in ["products", "variables", "eo-missions", "projects"]:
#     print(grp, [c.title for c in search("forest fires", type=grp, limit=2)])
# print(len(search("forest fires", theme="land", limit=2))) # one or more results expected - with theme = land
# print(len(search("forest fires", theme="ocean", limit=2))) # no results expected
# print(search(variable="burned-area")[0].title) # expect something that has a variable of fire
# print(search(keyword="Seasonal Fire Modeling")[0].title)
