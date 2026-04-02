import shutil
import tempfile
from pathlib import Path
from importlib import resources
import filecmp
import pytest
import os

from earthcode.validator import validate_catalog
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


def assertIsFile(path):
    if not Path(path).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(path))


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


def test_generate_template():
    test_dir = tempfile.mkdtemp()
    try:
        generate_template(
            project=True, workflow=True, experiment=True, product=True, target=test_dir
        )

        project = os.path.join(test_dir, "project.yaml")
        workflow = os.path.join(test_dir, "workflow.yaml")
        experiment = os.path.join(test_dir, "experiment.yaml")
        product = os.path.join(test_dir, "product.yaml")

        assertIsFile(project)
        assertIsFile(workflow)
        assertIsFile(experiment)
        assertIsFile(product)

        with resources.as_file(
            resources.files("earthcode.generators")
            .joinpath("templates")
            .joinpath("project.yaml")
        ) as expected_project:
            assert filecmp.cmp(project, expected_project), (
                "The project template is different from the expected one"
            )

        with resources.as_file(
            resources.files("earthcode.generators")
            .joinpath("templates")
            .joinpath("workflow.yaml")
        ) as expected_workflow:
            assert filecmp.cmp(workflow, expected_workflow), (
                "The workflow template is different from the expected one"
            )

        with resources.as_file(
            resources.files("earthcode.generators")
            .joinpath("templates")
            .joinpath("experiment.yaml")
        ) as expected_experiment:
            assert filecmp.cmp(experiment, expected_experiment), (
                "The experiment template is different from the expected one"
            )

        with resources.as_file(
            resources.files("earthcode.generators")
            .joinpath("templates")
            .joinpath("product.yaml")
        ) as expected_product:
            assert filecmp.cmp(product, expected_product), (
                "The product template is different from the expected one"
            )
    finally:
        shutil.rmtree(test_dir)


def test_packaged_schema_resources_exist():
    with resources.as_file(
        resources.files("earthcode").joinpath("schemas").joinpath("catalog.json")
    ) as schema_path:
        assert schema_path.is_file()


def test_generate_template_with_no_template_selected_logs_warning(caplog):
    test_dir = tempfile.mkdtemp()
    try:
        with caplog.at_level("WARNING"):
            generate_template(
                project=False,
                workflow=False,
                experiment=False,
                product=False,
                target=test_dir,
            )
        assert "No options selected." in caplog.text
    finally:
        shutil.rmtree(test_dir)


def test_generate_stac_with_no_template_selected_logs_warning(caplog):
    test_dir = tempfile.mkdtemp()
    try:
        with caplog.at_level("WARNING"):
            generate_stac(
                project=None,
                workflow=None,
                experiment=None,
                product=None,
                osc_path=test_dir,
            )
        assert "No template provided." in caplog.text
    finally:
        shutil.rmtree(test_dir)
