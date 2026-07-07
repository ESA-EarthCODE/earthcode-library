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


def test_transform():
    example = generate_example_product_analysis()
    res = product_audit_to_fair_dict(example)
    expected = {'fair:Findable_has_doi': True,
                'fair:Findable_rich_metadata': True,
                'fair:Findable_identifier': True,
                'fair:Findable_stac_assets': True,
                'fair:Findable_indexed': True,
                'fair:Findable_indexed_approved_metadata': True,
                'fair:Findable_indexed_approved_data': True,
                'fair:Accessible_general': True,
                'fair:Accessible_protocols': True,
                'fair:Accessible_files': 1.0,
                'fair:Interoperable_uses_formal_language': True,
                'fair:Interoperable_controlled_vocabularies': True,
                'fair:Interoperable_related_links': True,
                'fair:Interoperable_has_documentation': True,
                'fair:Reusable_rich_descriptions': True,
                'fair:Reusable_has_license': True,
                'fair:Reusable_workflow_exists': False,
                'fair:Reusable_cloud_assets_rate': 1.0,
                'fair:Reusable_has_visualisation': False,
                'fair:Reusable_has_access_example': True
                }
    assert res == expected