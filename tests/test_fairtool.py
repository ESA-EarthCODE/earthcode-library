import pystac
from earthcode.fairtool import analyse_product, ProductAuditResult


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
