import os
from pathlib import Path

import numpy as np
import pytest

import earthcode.search as search_module
from cli.generate_embeddings import build_embeddings
from earthcode.search import search


@pytest.fixture(scope="module", autouse=True)
def shared_model_runtime(tmp_path_factory):
    cache_root = tmp_path_factory.mktemp("model-cache")
    previous_source = os.environ.pop("EARTHCODE_MODEL_SOURCE", None)
    previous_file = os.environ.pop("EARTHCODE_MODEL_FILE", None)
    previous_cache = os.environ.get("EARTHCODE_MODEL_CACHE_DIR")
    os.environ["EARTHCODE_MODEL_CACHE_DIR"] = str(cache_root)
    search_module._embedding_runtime.clear()
    search_module._ds = None
    yield
    if previous_source is not None:
        os.environ["EARTHCODE_MODEL_SOURCE"] = previous_source
    if previous_file is not None:
        os.environ["EARTHCODE_MODEL_FILE"] = previous_file
    if previous_cache is not None:
        os.environ["EARTHCODE_MODEL_CACHE_DIR"] = previous_cache
    else:
        os.environ.pop("EARTHCODE_MODEL_CACHE_DIR", None)
    search_module._embedding_runtime.clear()
    search_module._ds = None


def test_mean_pool_and_normalize():
    hidden = np.asarray([[[1.0, 0.0], [3.0, 4.0], [10.0, 10.0]]], dtype=np.float32)
    mask = np.asarray([[1, 1, 0]], dtype=np.int64)

    pooled = search_module._mean_pool(hidden, mask)
    normalized = search_module._l2_normalize(pooled)

    expected = np.asarray([[2.0, 2.0]], dtype=np.float32)
    np.testing.assert_allclose(pooled, expected)
    np.testing.assert_allclose(
        normalized,
        expected / np.linalg.norm(expected, axis=1, keepdims=True),
    )


def test_search_basic():
    vectors = build_embeddings(["forest fires"])
    assert vectors.shape == (1, 384)

    results = search(collection_ids="seasfire-cube", limit=1)
    assert results, "no results returned"
    assert getattr(results[0], "id", None) == "seasfire-cube"

    results = search("forest fires", limit=3)
    assert len(results) > 0
    assert all(getattr(r, "id", None) for r in results)

    cache_root = search_module.MODEL_CACHE_DIR
    env_cache = os.getenv("EARTHCODE_MODEL_CACHE_DIR")
    if env_cache:
        cache_root = Path(env_cache)
    assert cache_root.exists()
    assert any(cache_root.iterdir())
    cached_bundle = search_module._get_cached_model_bundle()
    assert (cached_bundle / search_module.MODEL_FILE).exists()
    assert (cached_bundle / search_module.TOKENIZER_FILE).exists()

    results = search("chlorophyll", type="variables", limit=2)
    assert len(results) > 0


def test_bbox_intersects_hits_expected_product():
    alps_bbox = [5.95591129, 45.81799493, 10.49229402, 47.80846475]
    results = search("snow data", limit=10, bbox=alps_bbox)
    ids = [r.id for r in results]
    assert "binary-wet-snow-s14science-snow" in ids

    # Test that containment differs from intersects
    results_containment = search(
        "snow data", limit=10, bbox=alps_bbox, intersects=False
    )
    ids_containment = [r.id for r in results_containment]
    assert len(ids_containment) > 0
    assert "binary-wet-snow-s14science-snow" not in ids_containment


def test_combined_filters():
    # Test theme filter
    land_results = search("forest fires", theme="land", limit=5)
    assert len(land_results) > 0

    ocean_results = search("forest fires", theme="oceans", keyword="forest fires", limit=5)
    assert len(ocean_results) == 0

    # Test variable filter
    results = search(variable="burned-area", type="products", limit=5)
    ids = {r.id for r in results}
    assert "seasfire-cube" in ids

    # Test keyword filter
    results = search(keyword="seasonal fire modeling", type="products", limit=5)
    assert "seasfire-cube" in [r.id for r in results]
