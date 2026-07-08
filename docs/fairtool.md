# EarthCODE FAIR Audit Tool Documentation

## Overview: Understanding FAIR and Open Science

The FAIR principles dictate that scientific data must be **Findable**, **Accessible**, **Interoperable**, and **Reusable**. These principles ensure that datasets are not only discoverable by researchers but also structured in a way that allows automated systems and software to consume and analyze them without friction. 

The FairTools build on top of the OSC validator, and  analyzes SpatioTemporal Asset Catalog (STAC) products to evaluate their compliance against these principles. It parses metadata, validates links, checks domain registrations, and tests asset accessibility (actually attempting to open the files using libraries like `xarray`, `pandas`, and `rioxarray`).

For more details on community standards, visit the [EarthCODE FAIR and Open Science Best Practices Data Page](https://esa-earthcode.github.io/documentation/Community%20and%20Best%20Practices/FAIR%20and%20Open%20Science%20Best%20Practices/Data).

---

## FAIR Metrics and Calculation Logic

The following tables describe each test and berifly how it is carried out. 

### Findable (F)

Findability ensures that data and metadata are easily discoverable by both humans and machines, primarily through rich metadata and persistent identifiers.

| Key | Description | How it is Calculated |
| :--- | :--- | :--- |
| **`fair:Findable_has_doi`** | F1 — The dataset has an associated globally unique, persistent DOI. | Parses the STAC item for `sci:doi` and validates it by making a network request to `doi.org` to ensure it resolves (status 200). |
| **`fair:Findable_rich_metadata`** | F2 — The metadata is richly described using the OSC extension. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Findable_identifier`** | F3 — The metadata explicitly includes the identifier of the data it describes. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Findable_stac_assets`** | F3.1 — The metadata has per-file STAC items/assets including explicit identifiers. | Extracts the STAC `child` link and performs an HTTP request to ensure the nested catalog or item endpoints respond successfully. |
| **`fair:Findable_indexed`** | F4 — The (meta)data are registered or indexed in a searchable resource. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Findable_indexed_approved_metadata`** | F4.1 — The metadata are registered or indexed in an approved domain. | Extracts the `child` metadata link and cross-references its hostname against `APPROVED_METADATA_HOSTING_DOMAINS` (e.g., `*.esa.int`, `*.github.org`). |
| **`fair:Findable_indexed_approved_data`** | F4.2 — The data are registered or indexed in an approved domain. | Extracts the `via` data link and cross-references its hostname against `APPROVED_DATA_HOSTING_DOMAINS` (e.g., `zenodo.org`, `*.copernicus.eu`). |

### Accessible (A)

Accessibility guarantees that the data can be retrieved using standard, open protocols, even if authentication is required.

| Key | Description | How it is Calculated |
| :--- | :--- | :--- |
| **`fair:Accessible_general`** | A1 — Metadata are accessible over HTTPS via standard APIs. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Accessible_protocols`** | A1.1 — Protocols are open, free, and universally implementable. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Accessible_files`** | A1.2 — The percentage of randomly chosen assets successfully opened programmatically. | Navigates the `child` STAC link, samples a random subset of data assets (default 10), and attempts to load them into memory using data-specific Python readers (see below). Returns the float success rate (e.g., `1.0` for 100%). |

Tested file formats and readers:

| MIME type | Format | Reader used |
| :--- | :--- | :--- |
| `application/x-netcdf` | NetCDF | `xarray.open_dataset` |
| `application/vnd+zarr` | Zarr | `xarray.open_zarr` |
| `image/tiff` | TIFF / GeoTIFF | `rioxarray.open_rasterio` |
| `image/cog` | Cloud Optimized GeoTIFF | `rioxarray.open_rasterio` |
| `application/zip` | ZIP archive | `zipfile.ZipFile` |
| `application/pdf` | PDF | `open` |
| `text/plain` | Plain text | `open` |
| `text/csv` | CSV | `pandas.read_csv` |
| `application/vnd.apache.parquet` | Parquet | `pandas.read_parquet` |
| `application/vnd.apache.geoparquet` | GeoParquet | `geopandas.read_parquet` |
| `application/x-shapefile` | Shapefile | `geopandas.read_file` |
| `application/geo+json` | GeoJSON | `geopandas.read_file` |



### Interoperable (I)

Interoperability requires the data to integrate with other data, applications, or workflows for analysis, storage, and processing.

| Key | Description | How it is Calculated |
| :--- | :--- | :--- |
| **`fair:Interoperable_uses_formal_language`** | I1 — The metadata uses formal, accessible representation languages. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Interoperable_controlled_vocabularies`** | I2 — The dataset adopts controlled FAIR vocabularies via the STAC OSC extension. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Interoperable_related_links`** | I3 — The dataset has qualified links to related projects, experiments, etc. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Interoperable_has_documentation`** | I3 — The dataset has additional information such as guides or research papers. | Parses the STAC `links` array looking for a link where the `title` attribute exactly matches `"Documentation"`. |

### Reusable (R)

Reusability ensures that the data can be replicated and reused in distinct contexts.

| Key | Description | How it is Calculated |
| :--- | :--- | :--- |
| **`fair:Reusable_rich_descriptions`** | R1 — The dataset provides rich, domain-appropriate descriptions. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Reusable_has_license`** | R1.1 — The products are published with clear, standardized licenses. | **True by default.** Enforced strictly by the Open Science Catalog validator. |
| **`fair:Reusable_workflow_exists`** | R1.2 — The dataset has an associated workflow to record processing provenance. | Parses the STAC `links` array looking for a link with `rel="related"` and a `title` containing `"Experiment: "`. |
| **`fair:Reusable_cloud_assets_rate`** | R1.3 — The percentage of assets aligning with community cloud-native standards. | Evaluates the randomly sampled STAC assets (from the A1.2 check) against the `CLOUD_NATIVE_FORMATS` set (GeoParquet, COG, Zarr). Returns the percentage matching these formats. |
| **`fair:Reusable_has_visualisation`** | R1.4 — The dataset has an associated visualisation dashboard or tool. | Looks for a STAC link with relation `"visualisation"` and executes an HTTP request to ensure the URL resolves (status 200). |
| **`fair:Reusable_has_access_example`** | R1.5 — The dataset has an associated access example script or notebook. | Looks for a STAC link with relation `"example"` and executes an HTTP request to ensure the URL resolves (status 200). |

---

## Usage Examples

You can preview the score you will get on the OSC, using the code snippet below.

```python
import pystac
# Assuming the provided code block is saved as `fair_audit.py`
from earthcode.fairtool import analyse_product, product_audit_to_fair_dict

# ==========================================
# Scenario 1: Loading a Remote STAC Product
# ==========================================
target_product_location = "https://app-reverse-proxy.osc.earthcode.eox.at/open-science-catalog-metadata/products/waposal-waves/collection.json"

# Load the remote product directly using PySTAC
remote_product = pystac.Collection.from_file(target_product_location)

# Execute the core analysis logic (returns a ProductAuditResult dataclass)
audit_result = analyse_product(remote_product, max_asset_checks=10, seed=123)

# Transform the dataclass into the standardized FAIR dictionary schema
fair_metrics = product_audit_to_fair_dict(audit_result)
print("Remote Analysis Result:")
print(fair_metrics)


# ==========================================
# Scenario 2: Loading a Local STAC Product
# ==========================================
local_product_location = "./local_data/waposal-waves/collection.json"

# Load the local STAC file
local_product = pystac.Collection.from_file(local_product_location)

# Execute analysis on the local file
local_audit_result = analyse_product(local_product, max_asset_checks=10, seed=123)
local_fair_metrics = product_audit_to_fair_dict(local_audit_result)

print("\nLocal Analysis Result:")
print(local_fair_metrics)
```