"""Search interface for Lance vector store of Open Science Catalog items.

Provides semantic search across products, variables, missions, and projects using FastEmbed embeddings.

Returns:
    list[pystac.Collection | pystac.Catalog]: Search results as PySTAC objects.
"""

import json
from pathlib import Path
import shutil
import tempfile
import lance
import numpy as np
import pystac
from fastembed import TextEmbedding

LANCE_URI = "s3://pangeo-test-fires/vector_store_v5/"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
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
_model = None


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

    # dataset / model caches
    global _ds, _model
    if _ds is None or getattr(_ds, "uri", None) != LANCE_URI.rstrip("/") + "/":
        _ds = lance.dataset(
            LANCE_URI.rstrip("/") + "/", storage_options=LANCE_BASE_STORAGE_OPTIONS
        )
    if _model is None:
        try:
            _model = TextEmbedding(model_name=MODEL_NAME)
        except Exception as exc:
            if "NO_SUCHFILE" not in str(exc) and "NoSuchFile" not in str(exc):
                raise
            shutil.rmtree(Path(tempfile.gettempdir()) / "fastembed_cache", ignore_errors=True)
            _model = TextEmbedding(model_name=MODEL_NAME)

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

    if query and query.strip():
        vec = next(_model.embed([query]))

        tbl = _ds.scanner(
            columns=cols,
            filter=filt,
            nearest={
                "column": "embedding",
                "q": np.asarray(vec, dtype=np.float32),
                "k": limit,
            },
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
