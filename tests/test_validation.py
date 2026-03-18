from earthcode.validator import validate_catalog

def test_validation():
    catalog_path = '../open-science-catalog-metadata/'
    errors, error_files = validate_catalog(catalog_path)
    assert error_files == []
    assert errors == []