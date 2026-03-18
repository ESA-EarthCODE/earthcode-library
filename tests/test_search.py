import pytest

from earthcode.search import search


def test_search_basic():
    # Test collection ID search
    results = search(collection_ids="seasfire-cube", limit=1)
    assert results, "no results returned"
    assert getattr(results[0], "id", None) == "seasfire-cube"

    # Test basic semantic search
    results = search("forest fires", limit=3)
    assert len(results) > 0
    assert all(getattr(r, "id", None) for r in results)

    # Test variable search
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
