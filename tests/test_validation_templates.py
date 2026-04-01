import shutil
from pathlib import Path
from uuid import uuid4
import filecmp
import pytest
import pystac
import json

from earthcode.validator import validate_catalog
from earthcode.static import (
    generate_OSC_dummy_entries,
    add_item_link_to_product_collection,
    create_item,
)
from earthcode.git_add import (
    save_product_collection_to_catalog,
    save_workflow_record_to_osc,
    save_project_collection_to_osc,
    save_experiment_record_to_osc,
    save_item_to_product_collection,
    _add_link_if_missing,
)
from earthcode.static import create_item
from earthcode.metadata_input_definitions import ItemMetadata
from earthcode.generators import generate_template, generate_stac


### asummes a error free catalog
SOURCE_CATALOG = Path("../open-science-catalog-metadata/").resolve()


@pytest.fixture()
def catalog_root(tmp_path: Path) -> Path:

    if not SOURCE_CATALOG.exists():
        pytest.skip(f"Missing source catalog at {SOURCE_CATALOG}")

    target = tmp_path / "open-science-catalog-metadata"
    shutil.copytree(SOURCE_CATALOG, target, ignore=shutil.ignore_patterns(".*"))
    return target


def get_source_files():
    # return all files but ignore anything that starts with a .(dot)
    source_files = {
        f.relative_to(SOURCE_CATALOG)
        for f in SOURCE_CATALOG.rglob("*")
        if f.is_file()
        and not any(
            part.startswith(".") for part in f.relative_to(SOURCE_CATALOG).parts
        )
    }
    return source_files


def test_creation_and_validation(catalog_root: Path):

    generate_template(
        project=True,
        workflow=True,
        experiment=True,
        product=True,
        target=str(catalog_root.parent),
    )

    generate_stac(
        project=f"{catalog_root.parent / 'project.yaml'}",
        experiment=f"{catalog_root.parent / 'experiment.yaml'}",
        workflow=f"{catalog_root.parent / 'workflow.yaml'}",
        product=f"{catalog_root.parent / 'product.yaml'}",
        osc_path=str(catalog_root),
    )

    # assert that everything passes validation
    errors, error_files = validate_catalog(catalog_root)
    assert len(errors) == 0
    assert len(error_files) == 0

    # count updated , deleted and created files
    source_files = get_source_files()
    target_files = {
        f.relative_to(catalog_root) for f in catalog_root.rglob("*") if f.is_file()
    }

    created_files = target_files - source_files
    deleted_files = source_files - target_files
    common_files = source_files & target_files
    modified_files = set()

    for rel_path in common_files:
        src_file = SOURCE_CATALOG / rel_path
        tgt_file = catalog_root / rel_path

        # Setting shallow=False forces Python to compare the actual file contents
        # rather than just checking OS metadata like modification times.
        if not filecmp.cmp(src_file, tgt_file, shallow=False):
            modified_files.add(rel_path)

    assert len(created_files) == 4
    assert len(deleted_files) == 0
    assert len(modified_files) == 8
