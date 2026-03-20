import shutil
from pathlib import Path
from uuid import uuid4
import filecmp
import pytest
import pystac
import json

from earthcode.validator import validate_catalog
from earthcode.static import generate_OSC_dummy_entries, add_item_link_to_product_collection, create_item
from earthcode.git_add import (save_product_collection_to_catalog, 
                               save_workflow_record_to_osc, 
                               save_project_collection_to_osc, 
                               save_experiment_record_to_osc,
                               save_item_to_product_collection,
                               _add_link_if_missing)
from earthcode.static import create_item
from earthcode.metadata_input_definitions import ItemMetadata


### asummes a error free catalog
SOURCE_CATALOG = Path("../open-science-catalog-metadata/").resolve()


@pytest.fixture()
def catalog_root(tmp_path: Path) -> Path:

    if not SOURCE_CATALOG.exists():
        pytest.skip(f"Missing source catalog at {SOURCE_CATALOG}")

    target = tmp_path / "open-science-catalog-metadata"
    shutil.copytree(SOURCE_CATALOG, target, ignore=shutil.ignore_patterns('.*'))
    return target

def get_source_files():
    # return all files but ignore anything that starts with a .(dot)
    source_files = {
    f.relative_to(SOURCE_CATALOG) 
    for f in SOURCE_CATALOG.rglob('*') 
    if f.is_file() and not any(part.startswith('.') for part in f.relative_to(SOURCE_CATALOG).parts)
    }
    return source_files

def test_validation(catalog_root: Path):
    errors, error_files = validate_catalog(catalog_root)
    assert error_files == []
    assert errors == []


def test_creation_and_validation(catalog_root: Path):

    unique_suffix = f"+{uuid4().hex[:8]}"
    
    project, product, workflow, experiment = generate_OSC_dummy_entries(id_extension=unique_suffix)

    # assert that files are created
    assert not (catalog_root / f'projects/{project.id}/collection.json').exists()
    save_project_collection_to_osc(project, catalog_root)
    assert (catalog_root / f'projects/{project.id}/collection.json').exists()

    assert not (catalog_root / f'products/{product.id}/collection.json').exists()
    save_product_collection_to_catalog(product, catalog_root)
    assert (catalog_root / f'products/{product.id}/collection.json').exists()

    assert not (catalog_root / f'workflows/{workflow['id']}/record.json').exists()
    save_workflow_record_to_osc(workflow, catalog_root)
    assert (catalog_root / f'workflows/{workflow['id']}/record.json').exists()

    assert not (catalog_root / f'experiments/{experiment['id']}/record.json').exists()
    save_experiment_record_to_osc(experiment, catalog_root)
    assert (catalog_root / f'experiments/{experiment['id']}/record.json').exists()

    # assert that everything passes validation
    errors, error_files = validate_catalog(catalog_root)
    assert len(error_files) == 0
    assert len(errors) == 0

    # count updated , deleted and created files
    source_files = get_source_files()
    target_files = {f.relative_to(catalog_root) for f in catalog_root.rglob('*') if f.is_file()}

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


def return_item_metadata():
    
    import json
    import shapely
    import pandas as pd

    product_id = 'waposal-waves'
    zip_url = 'https://wgms.ch/downloads/GlaMBIE_Data_DOI_10.5904_wgms-glambie-2024-07.zip'
    collectionid = product_id
    bbox = [ -180.0, -90.0, 180.0, 90.0]
    geometry = json.loads(json.dumps(shapely.box(*bbox).__geo_interface__))
    data_time = pd.to_datetime('2024-07-16T00:00:00Z') # Release date of the dataset
    itemid = f"{collectionid}-zip_folder"
    item_license = "CC-BY-4.0"
    description = 'Dataset contents: The GlaMBIE dataset contains both the input data and the results to the exercise./n/nThe datasets are organised in the two main data folders, each with a more detailed data information file, and with subfolders containing the data in csv files./n/nCitation: The GlaMBIE Team (2024): Glacier Mass Balance Intercomparison Exercise (GlaMBIE) Dataset 1.0.0. World Glacier Monitoring Service (WGMS), Zurich, Switzerland. https://doi.org/10.5904/wgms-glambie-2024-07'
    data_url = zip_url
    data_mime_type = "application/zip"
    data_title = "GlaMBIE dataset archive (ZIP)"

    extra_fields = {
        "file:size": 2726298,
        "file:compression": "zip",
        "data:format": "CSV inside ZIP"
    }

    item_instance = ItemMetadata(
        itemid=itemid,
        geometry=geometry,
        data_time=data_time, 
        bbox=bbox,
        product_id=product_id,
        license=item_license,
        description=description,
        data_url=data_url,
        data_mime_type=data_mime_type,
        data_title=data_title,
        extra_fields=extra_fields
    )

    return item_instance


def test_item_add(catalog_root: Path):


    item_metadata = return_item_metadata()
    product_id = item_metadata.product_id
    data_title = item_metadata.data_title

    # create the item
    item = create_item(item_metadata)
    
    # load the product
    with open(catalog_root/f'products/{product_id}/collection.json', 'r', encoding='utf-8') as f:
            product_collection = json.load(f)
    product = pystac.Collection.from_dict(product_collection,
                                                        migrate=False,
                                                        root=None,
                                                        preserve_dict=True)
    
    # create product -> item link
    add_item_link_to_product_collection(product, item.id, data_title)
    
    # create other links and save
    save_item_to_product_collection(item, product, catalog_root)


    ## asserts

    # assert the item is created
    assert (catalog_root / f'products/{product.id}/{item.id}.json').exists()


    # count updated , deleted and created files
    source_files = get_source_files()
    target_files = {f.relative_to(catalog_root) for f in catalog_root.rglob('*') if f.is_file()}

    # count affected files
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

    # assert:
    # - only the product and item files are updated
    # - only the item file was created
    assert len(deleted_files) == 0
    assert created_files == set([Path(f'products/{product.id}/{item.id}.json')])
    assert modified_files == set([Path(f'products/{product.id}/collection.json')])
    
    # assert that everything passes validation
    errors, error_files = validate_catalog(catalog_root)
    assert len(error_files) == 0
    assert len(errors) == 0


def test_add_link_if_missing():

    product_id = 'glambie-dataset'
    itemid = f"{product_id}-zip_folder"
    data_title = "GlaMBIE dataset archive (ZIP)"

    # add to product collection if not already existing
    with open(SOURCE_CATALOG / f'products/{product_id}/collection.json', encoding='utf-8') as f:

        existing_product_collection = json.load(f)
        existing_product_collection = pystac.Collection.from_dict(existing_product_collection,
                                                         migrate=False,
                                                         root=None,
                                                         preserve_dict=True)
        initial_links = set(existing_product_collection.links)
        _add_link_if_missing(
            existing_product_collection,
            pystac.Link(rel="item", target=f"./{itemid}.json", media_type="application/json", title=data_title)
        )
        assert set(existing_product_collection.links) == initial_links


def test_add_fairtool_data_validation(catalog_root: Path):
    
    from earthcode.fairtool import generate_example_product_analysis, product_audit_to_fair_dict
    example = generate_example_product_analysis()
    result_dict = product_audit_to_fair_dict(example)

    file_dir = Path(catalog_root/f'products/{example.product_id}/collection.json')
    with open(file_dir, 'r', encoding='utf-8') as f:
        product_collection = json.load(f)
        product = pystac.Collection.from_dict(product_collection,
                                            migrate=False,
                                            root=None,
                                            preserve_dict=True)        
        product = product.to_dict(include_self_link=False, transform_hrefs=True)
        for k,v in result_dict.items():
            product[k] = v
        with open(file_dir, 'w', encoding='utf-8') as f:
            json.dump(product, f, ensure_ascii=False, indent=2)
    
    # count updated , deleted and created files
    source_files = get_source_files()
    target_files = {f.relative_to(catalog_root) for f in catalog_root.rglob('*') if f.is_file()}

    # count affected files
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

    # assert:
    # - only the product files is updated
    assert len(deleted_files) == 0
    assert  len(created_files) == 0
    assert modified_files == set([Path(f'products/{example.product_id}/collection.json')])
    
    # assert that everything passes validation
    errors, error_files = validate_catalog(catalog_root)
    assert len(error_files) == 0
    assert len(errors) == 0