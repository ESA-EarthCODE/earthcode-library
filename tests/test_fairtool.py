import pystac
from earthcode.fairtool import analyse_product, ProductAuditResult, generate_example_product_analysis, product_audit_to_fair_dict


def test_analyse_product():
    target_product_location = "https://app-reverse-proxy.osc.earthcode.eox.at/open-science-catalog-metadata/products/waposal-waves/collection.json"
    target_product = pystac.Collection.from_file(target_product_location)

    expected_result = ProductAuditResult(
        product_id="waposal-waves",
        via_href="https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/waposal_data.zip",
        child_href="https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/waposal/collection.json",
        has_doc=True,
        has_workflow=False,
        has_doi=True,
        via_response_ok=True,
        child_response_ok=True,
        via_domain_ok=True,
        has_access_example=True,
        has_visualisation=False,
        child_domain_ok=True,
        asset_audit={
            "child_link": "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/waposal/collection.json",
            "is_prr": False,
            "checked": [
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/CN-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/BN-CS2.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/FG-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/MT-S3B.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/FP-CS2.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/BN-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/MD-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/CN-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/FF-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/waposal/FG-S3A.zarr",
                    "type": "application/vnd+zarr",
                },
            ],
            "success_flags": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ],
            "success_rate": 1.0,
        },
        cloud_score=1.0,
    )

    result = analyse_product(target_product, seed=123)

    assert result == expected_result


def test_analyse_earthcare_frame_lightning_product():
    target_product_location = "https://esa-earthcode.github.io/open-science-catalog-metadata/products/earthcare-frame-lightning/collection.json"
    target_product = pystac.Collection.from_file(target_product_location)

    expected_result = ProductAuditResult(
        product_id="earthcare-frame-lightning",
        via_href="https://opensciencedata.esa.int/stac-browser/#/external/https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/storm-data/catalog.json",
        child_href="https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/storm-data/catalog.json",
        has_doc=False,
        has_workflow=False,
        has_doi=True,
        via_response_ok=True,
        child_response_ok=True,
        via_domain_ok=True,
        has_access_example=True,
        has_visualisation=True,
        child_domain_ok=True,
        asset_audit={
            "child_link": "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/storm-data/catalog.json",
            "is_prr": False,
            "checked": [
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2024_11.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2025_8.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2024_8.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_GLM_2025_10.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_clusters.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2024_9.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2024_10.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_GLM_2024_9.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_GLM_2024_11.parquet",
                    "type": "application/x-parquet",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/storm-data/EC_lightning_LI_2025_12.parquet",
                    "type": "application/x-parquet",
                },
            ],
            "success_flags": [True] * 10,
            "success_rate": 1.0,
        },
        cloud_score=1.0,
    )

    result = analyse_product(target_product, timeout=15, seed=123)

    assert result == expected_result


def test_analyse_ai4ais_larsen_c_ice_shelf_cube_product():
    target_product_location = "https://esa-earthcode.github.io/open-science-catalog-metadata/products/ai4ais-larsen-c-ice-shelf-cube/collection.json"
    target_product = pystac.Collection.from_file(target_product_location)

    expected_result = ProductAuditResult(
        product_id="ai4ais-larsen-c-ice-shelf-cube",
        via_href="./ai4ais-larsen-c-ice-shelf-cube-item.json",
        child_href=target_product_location,
        has_doc=False,
        has_workflow=False,
        has_doi=False,
        via_response_ok=False,
        child_response_ok=True,
        via_domain_ok=True,
        has_access_example=True,
        has_visualisation=False,
        child_domain_ok=True,
        asset_audit={
            "child_link": target_product_location,
            "is_prr": False,
            "checked": [
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/polar_cube_datasets/ai4ais/output_store.zarr/",
                    "type": "application/vnd+zarr",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/polar_cube_datasets/ai4ais/pig_output_store.zarr/",
                    "type": "application/vnd+zarr",
                },
            ],
            "success_flags": [True, True],
            "success_rate": 1.0,
        },
        cloud_score=1.0,
    )

    result = analyse_product(target_product, timeout=15, seed=123)

    assert result == expected_result


def test_analyse_bedrock_topography_antarctica_bedmachine_product():
    target_product_location = "https://esa-earthcode.github.io/open-science-catalog-metadata/products/bedrock-topography-antarctica-bedmachine/collection.json"
    target_product = pystac.Collection.from_file(target_product_location)

    expected_result = ProductAuditResult(
        product_id="bedrock-topography-antarctica-bedmachine",
        via_href="https://nsidc.org/data/nsidc-0756/versions/3",
        child_href="https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4DANTARCTICA/bedrock-topography-antarctica-bedmachine/catalog.json",
        has_doc=True,
        has_workflow=False,
        has_doi=True,
        via_response_ok=True,
        child_response_ok=True,
        via_domain_ok=True,
        has_access_example=True,
        has_visualisation=False,
        child_domain_ok=True,
        asset_audit={
            "child_link": "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4DANTARCTICA/bedrock-topography-antarctica-bedmachine/catalog.json",
            "is_prr": False,
            "checked": [
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/4DANTARCTICA/MEaSUREs_BedMachine_Antarctica_V003/BedMachineAntarctica-v3.nc",
                    "type": "application/x-netcdf",
                },
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/polar_cube_datasets/bedrock_topography/NSIDC-0756_BedMachineAntarctica_19700101-20191001_V04.1.zarr/",
                    "type": "application/vnd+zarr",
                },
            ],
            "success_flags": [True, True],
            "success_rate": 1.0,
        },
        cloud_score=0.5,
    )

    result = analyse_product(target_product, timeout=15, seed=123)

    assert result == expected_result


def test_analyse_seasfire_cube_product():
    target_product_location = "https://esa-earthcode.github.io/open-science-catalog-metadata/products/seasfire-cube/collection.json"
    target_product = pystac.Collection.from_file(target_product_location)

    expected_result = ProductAuditResult(
        product_id="seasfire-cube",
        via_href="https://zenodo.org/records/13834057",
        child_href=target_product_location,
        has_doc=False,
        has_workflow=False,
        has_doi=True,
        has_visualisation=True,
        has_access_example=True,
        via_response_ok=True,
        child_response_ok=True,
        via_domain_ok=True,
        child_domain_ok=True,
        asset_audit={
            "child_link": target_product_location,
            "is_prr": False,
            "checked": [
                {
                    "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/OSCAssets/seasfire/seasfire_v0.4.zarr/",
                    "type": "application/vnd+zarr",
                },
            ],
            "success_flags": [True],
            "success_rate": 1.0,
        },
        cloud_score=1.0,
    )

    result = analyse_product(target_product, timeout=15, seed=123)

    assert result == expected_result
    fair = product_audit_to_fair_dict(result)
    assert fair["fair:Accessible_files"] == 1.0
    assert fair["fair:Reusable_cloud_assets_rate"] == 1.0