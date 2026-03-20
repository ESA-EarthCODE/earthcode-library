import shutil
from pathlib import Path
import pytest
import papermill as pm

### asummes a error free catalog
SOURCE_CATALOG = Path("../open-science-catalog-metadata/").resolve()


@pytest.fixture()
def catalog_root(tmp_path: Path) -> Path:

    if not SOURCE_CATALOG.exists():
        pytest.skip(f"Missing source catalog at {SOURCE_CATALOG}")

    target = tmp_path / "open-science-catalog-metadata"
    shutil.copytree(SOURCE_CATALOG, target, ignore=shutil.ignore_patterns('.*'))
    return target


### this test should be run with -vv
def test_notebooks(catalog_root:Path):

    repo_root = Path(__file__).resolve().parents[1]
    notebooks_dir = repo_root / "guide"
    unique = "123456"
    project_id = f"4datlantic-ohc{unique}"
    project_title = "4DAtlantic-OHC"
    product_id = f"4d-atlantic-ohc-global{unique}"
    product_title = "Global Ocean Heat Content"
    workflow_id = f"4datlantic-wf{unique}"
    workflow_title = "4D-Atlantic-Workflow"
    experiment_id = f"4datlantic-experiment{unique}"

    project_params = {
        "catalog_root": str(catalog_root),
        "project_id": project_id,
        "project_title": project_title,
        "project_description": (
            "Given the major role of the ocean in the climate system, it is essential to characterize "
            "the temporal and spatial variations of its heat content."
        ),
        "project_status": "completed",
        "project_license": "various",
        "project_s": -90.0,
        "project_w": -180.0,
        "project_n": 90.0,
        "project_e": 180.0,
        "project_start_year": 2021,
        "project_start_month": 7,
        "project_start_day": 6,
        "project_end_year": 2025,
        "project_end_month": 6,
        "project_end_day": 12,
        "website_link": "https://www.4datlantic-ohc.org/",
        "eo4society_link": "https://eo4society.esa.int/projects/4datlantic-ohc/",
        "project_themes": ["oceans"],
        "to_name": "Roberto Sabia",
        "to_email": "roberto.sabia@esa.int",
        "consortium_members": [["Magellium", "magellium.fr"]],
    }

    product_params = {
        "catalog_root": str(catalog_root),
        "product_id": product_id,
        "product_title": product_title,
        "product_description": (
            "Given the major role of the ocean in the climate system, it is essential to characterize "
            "the temporal and spatial variations of its heat content."
        ),
        "product_status": "completed",
        "product_license": "CC-BY-4.0",
        "product_keywords": ["ocean", "heat", "content", "altimetry"],
        "product_s": [-90.0],
        "product_w": [-180.0],
        "product_n": [90.0],
        "product_e": [180.0],
        "product_start_year": 2021,
        "product_start_month": 1,
        "product_start_day": 1,
        "product_end_year": 2021,
        "product_end_month": 12,
        "product_end_day": 31,
        "product_region": "Global",
        "product_themes": ["oceans"],
        "product_missions": ["in-situ-observations", "grace-fo", "sentinel-6", "jason-3"],
        "product_variables": ["ocean-heat-budget"],
        "product_parameters": ["ocean_heat_content"],
        "product_doi": None,
        "project_id": project_id,
        "project_title": project_title,
        
    }

    workflow_params = {
        "catalog_root": str(catalog_root),
        "workflow_id": workflow_id,
        "workflow_title": workflow_title,
        "workflow_description": "This describes the OHC workflow",
        "workflow_keywords": ["ocean", "heat", "content"],
        "workflow_license": "CC-BY-4.0",
        "workflow_formats": ["netcdf64"],
        "project_id": project_id,
        "project_title": project_title,
        "workflow_themes": ["oceans"],
        "workflow_contracts_info": [("Magellium", "contact@magellium.fr")],
        "codeurl": "https://github.com/ESA-EarthCODE/open-science-catalog-metadata",
        "workflow_doi": None,
        "include_workflow_bbox": False,
        "include_workflow_time": False,
    }

    experiment_params = {
        "catalog_root": str(catalog_root),
        "experiment_id": experiment_id,
        "experiment_title": "4D-Atlantic-Experiment",
        "experiment_description": "This describes the OHC experiment",
        "experiment_license": "CC-BY-SA-4.0",
        "experiment_keywords": ["ocean", "heat", "content"],
        "experiment_formats": ["GeoTIFF"],
        "experiment_themes": ["oceans"],
        "experiment_input_parameters_link": "https://github.com/deepesdl/cube-gen",
        "experiment_enviroment_link": "https://github.com/deepesdl/cube-gen",
        "workflow_id": workflow_id,
        "workflow_title": workflow_title,
        "product_id": product_id,
        "product_title": product_title,
        "experiment_contacts": None,
        "include_experiment_bbox": False,
        "include_experiment_time": False,
    }

    prr_collection_params = {
        "item_link" : "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
        "documentation_link": "https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf",
        "license_link": "https://www.aviso.altimetry.fr/fileadmin/documents/data/License_Aviso.pdf",
        "access_link": "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
        "product_id": product_id,
        "catalog_root": str(catalog_root),
    }

    remote_item_params = {       
        "item_title": product_title,
        "item_id": f"{product_id}-zip_folder",
        "item_bbox": [-180.0, -90.0, 180.0, 90.0],
        "item_datetime": "2024-07-16T00:00:00Z",
        "item_license": "CC-BY-4.0",
        "item_description": (
            "Dataset contents for notebook-run validation item."
        ),
        "item_data_url": "https://wgms.ch/downloads/GlaMBIE_Data_DOI_10.5904_wgms-glambie-2024-07.zip",
        "item_data_mime_type": "application/zip",
        "item_data_title": "GlaMBIE dataset archive (ZIP)",
        "item_extra_fields": {
            "file:size": 2726298,
            "file:compression": "zip",
            "data:format": "CSV inside ZIP",
        },

        "product_id": product_id,
        "catalog_root": str(catalog_root),
    }
   

    # execute notebooks, since each runs a validation on the entire catalog
    # we are also checking for newly introduced errors.
   
   
    # project
    pm.execute_notebook(
            input_path=str(notebooks_dir / "1.Project.ipynb"),
            output_path=None,
            parameters=project_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )

    # product
    pm.execute_notebook(
            input_path=str(notebooks_dir / "2.0.Product.ipynb"),
            output_path=None,
            parameters=product_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )

    # add PRR product items
    pm.execute_notebook(
            input_path=str(notebooks_dir / "2.1.Product_files_PRR.ipynb"),
            output_path=None,
            parameters=prr_collection_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )

    # add remote product items
    pm.execute_notebook(
            input_path=str(notebooks_dir / "2.1.Product_files_self_hosted.ipynb"),
            output_path=None,
            parameters=remote_item_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )

    # workflow
    pm.execute_notebook(
            input_path=str(notebooks_dir / "3.Workflow.ipynb"),
            output_path=None,
            parameters=workflow_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )

    # experiment
    pm.execute_notebook(
            input_path=str(notebooks_dir / "4.Experiment.ipynb"),
            output_path=None,
            parameters=experiment_params,
            kernel_name="python3",
            cwd=str(repo_root),
            log_output=True,
    )
