
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import fnmatch
from urllib.parse import urlparse
import requests
import pystac

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union, Any
from pathlib import Path

from fsspec.implementations.http import HTTPFileSystem
from zarr.storage import ZipStore
from xarray import open_datatree
import rioxarray
import xarray
import geopandas as gpd
import pandas as pd
import zipfile
import csv


READERS = {
    # xarray
    "application/x-netcdf": xarray.open_dataset,
    "application/vnd+zarr": xarray.open_zarr,

    # rioxarray
    "image/tiff": rioxarray.open_rasterio,
    "image/cog": rioxarray.open_rasterio,  # Cloud Optimized GeoTIFF (COG)

    # Python standard libs
    "application/zip": zipfile.ZipFile,
    "application/pdf": open,
    "text/plain": open,

    # pandas
    "text/csv": pd.read_csv,
    "application/vnd.apache.parquet": pd.read_parquet,

    # geopandas
    "application/x-shapefile": gpd.read_file,
    "application/vnd.apache.geoparquet": gpd.read_parquet,
    "application/geo+json": gpd.read_file,
}

APPROVED_DATA_HOSTING_DOMAINS = [
    "*.esa.int",
    "s3.waw4-1.cloudferro.com",
    "zenodo.org",
    "doi.org",
    "*.pangaea.de",
    "*.copernicus.eu",
    "*.ac.uk",
]

APPROVED_METADATA_HOSTING_DOMAINS = [
    "*.esa.int",
    "s3.waw4-1.cloudferro.com",
    "*.github.org",
]

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0"

CLOUD_NATIVE_FORMATS = set([
    "application/vnd.apache.geoparquet",
    "image/cog",
    "application/vnd+zarr"
])

fair_descriptions = {

    # --- FINDABLE ---
    "fair:Findable_has_doi": "F1 — The dataset has an associated globally unique, persistent DOI.",
    "fair:Findable_rich_metadata": "F2 — The metadata is richly described using the OSC extension.",
    "fair:Findable_identifier": "F3 — The metadata clearly and explicitly include the identifier of the data it describes",
    "fair:Findable_stac_assets": "F3.1 — The metadata has per-file STAC items or assets that explicitly include the identifier of the data it describes.",
    "fair:Findable_indexed": "F4 — The (meta)data are registered or indexed in a searchable resource.",
    "fair:Findable_indexed_approved_metadata": "F4.1 — The metadata are registered or indexed in an approved domain.",
    "fair:Findable_indexed_approved_data": "F4.2 — The data are registered or indexed in an approved domain.",

    # --- ACCESSIBLE ---
    "fair:Accessible_general": "A1 —  Metadata are accessible over HTTPS via STAC API, OGC CSW (2.0.2/3.0.0), OpenSearch, OAI-PMH, or SRU.",
    "fair:Accessible_protocols": "A1.1 — Protocols are open, free, and universally implementable.",
    "fair:Accessible_files": "A1.2 — The percentage of randomly chosen assets that were successfully opened programatically.",
    "fair:Accessible_metadata": "A2 — Metadata are accessible, even when the data are no longer available",

    # --- INTEROPERABLE ---
    "fair:Interoperable_uses_formal_language": "I1 — The metadata uses formal, accessible representation languages (e.g., JSON in STAC).",
    "fair:Interoperable_controlled_vocabularies": "I2 — The dataset adopts controlled FAIR vocabularies aligned with CF Standard Names and GCMD Keywords via the STAC OSC extension.",
    "fair:Interoperable_related_links": "I3 — The dataset has qualified links to related projects, experiments, themes, and variables.",
    "fair:Interoperable_has_documentation": "I3 — The dataset has additional information such as guides, research papers and others.",

    # --- REUSABLE ---
    "fair:Reusable_rich_descriptions": "R1 — The dataset provides rich, domain-appropriate descriptions about variables, themes, and spatial/temporal extent.",
    "fair:Reusable_has_license": "R1.1 — The products are published with clear, standardized licenses.",
    "fair:Reusable_workflow_exists": "R1.2 — The dataset has an associated workflow to record processing provenance.",
    "fair:Reusable_cloud_assets_rate": "R1.3 — The percentage of assets that align with community standards by being in cloud-native formats (e.g., Zarr, COG, GeoParquet).",
    "fair:Reusable_has_visualisation": "R1.4 — The dataset has an associated visualisation dashboard, notebooks or tools.",
    "fair:Reusable_has_access_example": "R1.5 — The dataset has an associated access example script or notebook.",

}


@dataclass
class ProductAuditResult:
    """
    Holds the complete analysis result for a single Product.
    """
    product_id: str
    
    # Metadata Links
    via_href: Optional[str]
    child_href: Optional[str]
    
    # Flags
    has_doc: bool
    has_workflow: bool
    has_doi: bool
    has_visualisation : bool
    has_access_example: bool
    
    # Validation Results (Access)
    via_response_ok: bool
    child_response_ok: bool
    
    # Validation Results (Domains)
    via_domain_ok: bool
    child_domain_ok: bool
    
    # Asset Audit Data
    asset_audit: Optional[Dict[str, Any]] = None
    cloud_score: float = 0.0



# ----------------------------- Helpers ----------------------------------------

def _is_prr(link: str) -> bool:
    return "https://eoresults.esa.int" in link

def _is_creodias(link: str) -> bool:
    return "https://s3.waw4-1.cloudferro.com/" in link

def try_response(url: str, allow_redirects: bool = True, timeout: int = 5) -> requests.Response:
    """
    HEAD a URL (optionally retry with UA) and return the Response.
    """
    headers = {}
    # First attempt: HEAD
    try:
        resp = requests.head(url, allow_redirects=allow_redirects, timeout=timeout)
        if resp.status_code == 200:
            return resp
    except requests.RequestException:
        pass # Fall through to retry logic

    # Retry logic
    if _is_prr(url):
        resp = requests.get(url, headers=headers, allow_redirects=allow_redirects, timeout=timeout)
    else:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
        resp = requests.head(url, headers=headers, allow_redirects=allow_redirects, timeout=timeout)
            
    return resp

def check_domain(url: str, allowed_patterns: Sequence[str]) -> bool:
    """Check if a URL's hostname matches allowed wildcard patterns."""
    if not url:
        return False
    hostname = urlparse(url).hostname or ""
    for pattern in allowed_patterns:
        if fnmatch.fnmatch(hostname, pattern):
            return True
    return False

def check_product_doi(product, timeout: int = 5) -> bool:
    """
    Check whether a STAC product item has a DOI and whether it resolves.
    """
    try:
        product_dict = product.to_dict()
        doi_value = product_dict.get("sci:doi")
        if doi_value:
            doi_url = f"https://doi.org/{doi_value}"
            response = try_response(doi_url, timeout=timeout)
            return response.status_code == 200
    except Exception:
        return False
    return False

def _load_zip_zarr(url: str, **kwargs):
    class HttpZipStore(ZipStore):  # type: ignore
        def __init__(self, path) -> None:
            super().__init__(path="", mode="r")
            self.path = path

    fs = HTTPFileSystem(asynchronous=False, block_size=10000)  # type: ignore
    zf = fs.open(url)
    store = HttpZipStore(zf)
    return open_datatree(store, engine="zarr", **kwargs)

def get_resolve_href(feat, asset):

    # check for cloudferro assets
    if asset['href'].startswith('s3://'):
            return 'https://s3.waw4-1.cloudferro.com/' + asset['href']  
    elif asset['href'][0] != '/':
            return asset['href']
    else:
        root_href = feat['links'][0]['href']
        scheme = root_href.index('//') + 2
        root_url = root_href[0: root_href[scheme:].index('/') + scheme]
        return root_url + asset['href']

def load_items_from_child_link(link: str, max_items: int = 1000) -> Tuple[bool, List[Tuple[str, Optional[str]]]]:
    prr = _is_prr(link)
    
    if prr:
        items = pystac.ItemCollection.from_file(link + "/items?limit=" + str(max_items))
    else:
        stac_obj = pystac.STACObject.from_file(link)
        items = pystac.ItemCollection([next(stac_obj.get_items(recursive=True)) for _ in range(max_items)])
    
    items_dict = items.to_dict()
    out: List[Tuple[str, Optional[str]]] = []
    
    for feat in items_dict.get("features", []):
        assets = feat.get("assets", {})
        for _name, a in assets.items():
            if a.get("roles") == ["data"]:
                out.append((get_resolve_href(feat, a), a.get("type")))

    return prr, out

def sample_assets(
    assets: Sequence[Tuple[str, Optional[str]]],
    max_checks: int,
    seed: Optional[int] = None,
) -> List[Tuple[str, Optional[str]]]:
    if seed is not None:
        random.seed(seed)
    if len(assets) <= max_checks:
        return list(assets)
    return random.sample(list(assets), k=max_checks)

def check_asset_readable(href: str, mime_type: Optional[str], is_prr: bool) -> bool:
    mtype = mime_type or ""
    reader = READERS.get(mtype)

    try:
        test_href = href
        if is_prr:
            if not href.startswith("https://eoresults.esa.int/"):
                test_href = "https://eoresults.esa.int/" + href.lstrip("/")
            if mtype == "application/vnd+zarr":
                _load_zip_zarr(test_href)
                return True
            if mtype == "application/x-netcdf":
                xarray.open_dataset(test_href + "#mode=bytes", decode_cf=False, decode_times=False, decode_coords=False, decode_timedelta=False)
                return True
            if reader:
                reader(test_href)  # type: ignore
                return True
            return False

        # non-PRR
        if mtype == "application/x-netcdf":
            test_href = href + "#mode=bytes"
        if reader is None:
            return False
        reader(test_href)  # type: ignore
        return True

    except Exception as e:
        logging.debug("Asset read failed for %s (%s): %s", href, mtype, e)
        return False



# ----------------------------- Core logic -------------------------------------

def analyse_product(
    productCollection: Union[pystac.Item, pystac.Collection],
    timeout: int = 5,
    max_asset_checks: int = 10,
    seed: Optional[int] = None
) -> ProductAuditResult:
    """
    Analyzes a single product (Item or Collection) entirely.
    
    Performs:
    1. Metadata extraction (links, docs, workflow, visualisation, example)
    2. Responsiveness checks (HTTP HEAD on via/child)
    3. Domain validation
    4. Asset sampling and reading tests
    5. Cloud native scoring
    """

    product_id = productCollection.id
    
    # 1. Extract Links
    via_link = productCollection.get_single_link("via")
    via_href = via_link.href if via_link else None

    child_link = productCollection.get_single_link("child")
    child_href = child_link.href if child_link else None

    # 2. Check Documentation / Workflow
    has_doc = False
    has_workflow = False
    for link in productCollection.get_links():
        title = getattr(link, "title", None)
        if title == "Documentation":
            has_doc = True
        if link.rel == "related" and isinstance(title, str) and "Experiment: " in title:
            has_workflow = True

    
    # check visualisation is present and accessible
    vis_link = productCollection.get_single_link("visualisation")
    vis_href = vis_link.href if vis_link else None

    # check access example notebook is present and accessible
    example_link = productCollection.get_single_link("example")
    example_href = example_link.href if example_link else None

    # 3. Check DOI
    has_doi = check_product_doi(productCollection, timeout=timeout)

    # 4. Check Response Status 
    # (Access)
    via_ok = False
    if via_href:
        try:
            via_ok = try_response(via_href, timeout=timeout).status_code == 200
        except requests.RequestException:
            via_ok = False
    
    # (Visualisation)
    vis_ok = False
    if vis_href:
        try:
            vis_ok = try_response(vis_href, timeout=timeout).status_code == 200
        except requests.RequestException:
            vis_ok = False
    
    # Example
    example_ok = False
    if example_href:
        try:
            example_ok = try_response(example_href, timeout=timeout).status_code == 200
        except requests.RequestException:
            example_ok = False

    # Child
    child_ok = False
    if child_href:
        try:
            child_ok = try_response(child_href, timeout=timeout).status_code == 200
        except requests.RequestException:
            child_ok = False

    # 5. Check Domains
    via_domain_ok = False
    if via_href:
        via_domain_ok = check_domain(via_href, APPROVED_DATA_HOSTING_DOMAINS)
        
    child_domain_ok = False
    if child_href:
        child_domain_ok = check_domain(child_href, APPROVED_METADATA_HOSTING_DOMAINS)

    # 6. Asset Audit (Child link traversal)
    asset_audit = None
    cloud_score = 0.0

    if child_href:
        try:
            is_prr, assets = load_items_from_child_link(child_href, max_items=max_asset_checks*10)
            
            # Default assumption: assume NetCDF when type is missing
            assets_norm: List[Tuple[str, Optional[str]]] = [
                (href, mtype if mtype is not None else "application/x-netcdf")
                for (href, mtype) in assets
            ]

            subset = sample_assets(assets_norm, max_checks=max_asset_checks, seed=seed)
            successes = [check_asset_readable(h, t, is_prr) for (h, t) in subset]
            
            # Calculate Asset Stats
            asset_audit = {
                "child_link": child_href,
                "is_prr": is_prr,
                "checked": [{"href": h, "type": t} for (h, t) in subset],
                "success_flags": successes,
                "success_rate": (sum(successes) / len(successes)) if subset else None,
            }

            # Calculate Cloud Score
            # Score 1 if format is cloud native, else 0. Average over checked assets.
            if subset:
                cn_scores = [1 if t in CLOUD_NATIVE_FORMATS else 0 for (_, t) in subset]
                cloud_score = sum(cn_scores) / len(cn_scores)

        except Exception as e:
            asset_audit = {
                "child_link": child_href,
                "error": f"Failed to load items: {e}",
                "checked": [],
                "success_flags": [],
            }
            cloud_score = 0.0

    return ProductAuditResult(
        product_id=product_id,
        via_href=via_href,
        child_href=child_href,
        has_doc=has_doc,
        has_workflow=has_workflow,
        has_doi=has_doi,
        has_visualisation=vis_ok,
        has_access_example=example_ok,
        via_response_ok=via_ok,
        child_response_ok=child_ok,
        via_domain_ok=via_domain_ok,
        child_domain_ok=child_domain_ok,
        asset_audit=asset_audit,
        cloud_score=cloud_score
    )

def product_audit_to_fair_dict(result: ProductAuditResult):
    """
    Converts a ProductAuditResult object into a dictionary with specific 'fair:' keys.
    Some checks are true by default, since the OSC validator guarantees them.
    """
    
    # Extract success rate safely; default to 0.0 or None if no audit occurred
    accessible_files_rate = 0.0
    if result.asset_audit and result.asset_audit.get("success_rate") is not None:
        accessible_files_rate = result.asset_audit["success_rate"]

    return {
        
        # --- FINDABLE ---
        "fair:Findable_has_doi": result.has_doi,
        "fair:Findable_rich_metadata": True,
        "fair:Findable_identifier": True,
        "fair:Findable_stac_assets": result.child_response_ok,
        "fair:Findable_indexed": True,
        "fair:Findable_indexed_approved_metadata": result.child_domain_ok,
        "fair:Findable_indexed_approved_data": result.via_domain_ok,

        # --- ACCESSIBLE ---
        "fair:Accessible_general": True,
        "fair:Accessible_protocols": True,
        "fair:Accessible_files": accessible_files_rate,

        # --- INTEROPERABLE ---
        "fair:Interoperable_uses_formal_language": True,
        "fair:Interoperable_controlled_vocabularies": True,
        "fair:Interoperable_related_links": True,
        "fair:Interoperable_has_documentation": result.has_doc,

        # --- REUSABLE ---
        "fair:Reusable_rich_descriptions": True,
        "fair:Reusable_has_license": True,
        "fair:Reusable_workflow_exists": result.has_workflow,
        "fair:Reusable_cloud_assets_rate": result.cloud_score,
        "fair:Reusable_has_visualisation": result.has_visualisation,
        "fair:Reusable_has_access_example": result.has_access_example,


    }



def run_audit(
    catalog_path: str,
    max_checks: int = 10,
    seed: Optional[int] = None,
    timeout: int = 5,
) -> Dict[str, object]:
    """
    High-level orchestration:
      1) Load catalog
      2) Loop through products and call analyse_product on each
      3) Aggregate results into a summary dictionary
    """
    catalog = pystac.Catalog.from_file(catalog_path)
    products_catalog = catalog.get_child("products")
    if products_catalog is None:
        raise ValueError("Catalog has no child named 'products'.")

    # Aggregation containers
    access_responses: Dict[str, bool] = {}
    child_responses: Dict[str, bool] = {}
    data_domain_ok: Dict[str, bool] = {}
    metadata_domain_ok: Dict[str, bool] = {}
    has_doc_map: Dict[str, bool] = {}
    has_workflow_map: Dict[str, bool] = {}
    has_doi_map: Dict[str, bool] = {}
    per_child_asset_checks: Dict[str, Dict[str, object]] = {}
    cloud_assets_score: Dict[str, float] = {}
    num_products_with_via = 0
    num_products_with_child = 0

    # Main Loop
    for product in products_catalog.get_children():
        
        # Call the unified analysis function
        result = analyse_product(
            product, 
            timeout=timeout, 
            max_asset_checks=max_checks, 
            seed=seed
        )

        # Aggregate Results
        if result.via_href:
            num_products_with_via += 1
            access_responses[result.product_id] = result.via_response_ok
            data_domain_ok[result.product_id] = result.via_domain_ok
            
        if result.child_href:
            num_products_with_child += 1
            child_responses[result.product_id] = result.child_response_ok
            metadata_domain_ok[result.product_id] = result.child_domain_ok
            
            if result.asset_audit:
                per_child_asset_checks[result.product_id] = result.asset_audit
                cloud_assets_score[result.product_id] = result.cloud_score

        has_doc_map[result.product_id] = result.has_doc
        has_workflow_map[result.product_id] = result.has_workflow
        has_doi_map[result.product_id] = result.has_doi

    return {
        "summary": {
            "num_products_with_via": num_products_with_via,
            "num_products_with_child": num_products_with_child,
        },
        "access_ok": access_responses,
        "child_ok": child_responses,
        "data_domain_ok": data_domain_ok,
        "metadata_domain_ok": metadata_domain_ok,
        "has_documentation": has_doc_map,
        "has_workflow": has_workflow_map,
        "has_doi": has_doi_map,
        "per_child_asset_checks": per_child_asset_checks,
        "cloud_assets": cloud_assets_score,
    }



def generate_example_product_analysis():
    return ProductAuditResult(
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
        has_access_example=True,
        has_visualisation=False,
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


def add_fairtool_results_to_product(product_collection_path):
    pystac.set_stac_version('1.0.0')
    product_dir = Path(product_collection_path)

    # read the product data and update with the fairtool results
    with open(product_dir, 'r', encoding='utf-8') as f:
        product_collection = json.load(f)
        product = pystac.Collection.from_dict(product_collection,
                                            migrate=False,
                                            root=None,
                                            preserve_dict=True)
        result = analyse_product(product, seed=123)
        result_dict = product_audit_to_fair_dict(result)
        product = product.to_dict(include_self_link=False, transform_hrefs=True)
        for k,v in result_dict.items():
            product[k] = v
    
    return product