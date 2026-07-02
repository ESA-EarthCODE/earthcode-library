# Contributing to the Open Science Catalog

## 1. Intro

This page explains how to make contribute data and metadata to the Open Science Catalog (OSC) using the `earthcode-library`.
It describes the main concepts, the metadata and data the OSC needs from a contributor, and where the EarthCODE Library helps.

Once you are familiar with the process, start working by :
1. Creating a local or remote enviroment
2. **Creating your own script or jupyter notebook** to generate the metadata
3. Open a PR against the Open Science Catalog, to start the review process.

## 2. What is the Open Science Catalog?

The Open Science Catalog indexes Earth Observation research
outputs from ESA-funded activities. It helps users find projects, datasets,
workflows, experiments, variables, EO missions, themes, and the files or assets
that make up published scientific products.

The OSC is built around STAC, the SpatioTemporal Asset Catalog standard. STAC
provides a common way to describe geospatial and temporal data, the assets that
belong to it, and the links between related resources.

The main OSC concepts are:

- `Project`: the ESA Earth Observation Programme activity or research context.
  A project records the official title, description, time span, spatial extent,
  themes, license, Technical Officer contact, website links, and consortium
  members.
- `Product / Dataset`: the scientific output that users should discover and
  access. A project can have one product or many products.
- `Files / data`: the actual assets behind a product. Each file, archive, scene,
  or time-specific data object should be described with file-level metadata,
  usually as a STAC Item.
- `Workflow / code`: the reusable scientific code, processing logic, or method
  used to generate a product.
- `Experiment`: a specific execution or implementation of a workflow that
  generated a product. It links the product, workflow, input parameters,
  runtime environment, formats, themes, and license.
- `Variables`: controlled terms that describe the geophysical, climate, or
  environmental quantities represented by a product.
- `EO missions`: controlled terms that describe the observing missions or source
  categories used to generate the product. Products based on in-situ data or
  numerical models should use the relevant OSC source category.
- `Themes`: broad OSC science domains used for discovery, such as atmosphere,
  cryosphere, land, oceans, or solid earth.
- `Licenses`: required metadata for publishable projects, products, workflows,
  experiments, and files. Missing or unclear licenses can block publication.

The important idea is that OSC records are connected. A product links back to a
project. File-level metadata links assets to the product. A workflow explains the
method. An experiment explains a particular execution of that method. Together
these records make the output discoverable, reusable, and reviewable.

## 3. Contributing to the Open Science Catalog

To process your data and publish it on the Open Science Catalog, we need:

1. Your data hosted in a long-term repository in a format suitable for object storage and streaming.

   Data is easiest to publish when it is already stored at stable URLs and is in
   a cloud-optimised format. The preferred formats are `Zarr`, `COG`, and `Parquet`.


| Format | Best for | Why it matters in object storage |
| --- | --- | --- |
| Zarr | Multidimensional arrays such as time/depth/y/x cubes | Chunked reads let analysis load only the pieces it needs. |
| Cloud Optimized GeoTIFF (COG) | Single rasters or raster stacks exposed as files | Internal tiling and overviews enable efficient range reads and quicklooks. |
| GeoParquet | Vector geometries and tabular point data | Columnar storage, embedded geospatial metadata, and fast filtering. |


   > See the examples for conversion patterns. 
   
   > ** If your data is not yet in a suitable format, the EarthCODE team can help you decide what
   conversion or hosting path is appropriate. If you are at this stage, email the EarthCODE team at earthcode@esa.int **

   > If your data is NOT hosted on object storage, the EarthCODE team can help move your data to ESA object storage. You still need to complete all the steps below and open the PR, to provide enough information to support you.

2. Metadata information about all aspects of the data and project described in section 2.

3. A PR against the `open-science-catalog-metadata` repostiory with the information from 1), 2).


## 4. Using the EarthCODE Library

The EarthCODE Library helps create, save, validate, and search OSC metadata. It
does not replace scientific judgement: contributors still need to provide
accurate descriptions, licenses, extents, variables, missions, workflow links,
experiment context, and file-level metadata.

Use the library and follow the contribution path below.

1. Set up the EarthCODE Library environment locally or remotely.

   You can contribute from a local environment or from an EarthCODE Workspace.

   - Use the local setup how-to guide if you want to install the library, clone
     your OSC metadata fork, run notebooks locally, and open a pull request from
     your own machine.

   - Use the workspace setup how-to guide if you want to work in the EarthCODE
     Workspace with JupyterLab and the surrounding platform tooling.

2. ** Create a new notebook ** to add project, product, workflow, and experiment metadata to your `open-science-catalog-metadata` fork.

   Start with the project because it is the top-level context for the
   contribution. Then add the product or products that describe the datasets.
   Add workflow metadata when code or processing logic should be published. Add
   experiment metadata when a specific workflow execution generated a specific
   product.


3. Generate the STAC Items for each file in each product dataset you specified in step 2).

   Product metadata describes the dataset as a whole. STAC Item metadata
   describes the files that make up that dataset. This is often the most
   time-consuming part of a contribution, because each asset needs enough
   information to be usable: stable URL, title, description, timestamp, spatial
   footprint, bounding box, MIME type, license, and any useful extra fields.

   The tutorials show how to generate STAC Item metadata for the main supported file
   formats:

   - Generate STAC Item metadata for `Zarr` data - `docs/tutorials/zarr_file_metadata.ipynb`.
   - Generate STAC Item metadata for `COG` data - `docs/tutorials/zarr_file_metadata.ipynb`.
   - Generate STAC Item metadata for `Parquet` data - `docs/tutorials/zarr_file_metadata.ipynb`.


   > If your require the data to be hosted and it does not have a stable URL:
      1. You still need to complete the project, product, workflow, experiment and file metadata steps.
      2. However, change the file remote url to the filename. The earthcode team will change it once the data is hosted online.
      3. Open the pull request with the OSC metadata. ( see below)

   > If you have more than 600 files:
     1. Create a self-contained STAC Collection and add the Items to it.
     2. Open the pull request with the OSC metadata.
     3. Zip the self-contained collection and send it to the EarthCODE team.
     4. The EarthCODE team will host the collection and update the links

5. Open a pull request.

   When the metadata is generated and validation passes, open a pull request
   against the main `open-science-catalog-metadata` repository.

   The pull request should contain only the intended OSC metadata changes. It
   should include a clear title and description so the EarthCODE Data Steward
   team can understand what is being added or changed.

   After the pull request is opened, automatic checks validate the metadata. The
   Data Steward team reviews the contribution and may ask for corrections before
   merging it into the published catalog.

## Tutorials

The tutorials demonstrate how the different pieces fit together with example data:

- A complete worked example showing how a project, product, workflow,
  experiment, and product-file metadata are contributed to the OSC - `docs/tutorials/end_to_end_subglacial_lakes.ipynb`. The script/notebook you create will look something like this.

- A tutorial on how to search existing OSC data so contributors can reuse
  existing projects, variables, EO missions, themes, and examples where
  appropriate - `./tutorials/earthcode_data_discovery.ipynb`.

- How to generate STAC Item metadata for the main supported file formats:
   - Generate STAC Item metadata for `Zarr` data - `docs/tutorials/zarr_file_metadata.ipynb`.
   - Generate STAC Item metadata for `COG` data - `docs/tutorials/cog_file_metadata.ipynb`.
   - Generate STAC Item metadata for `Parquet` data - `docs/tutorials/parquet_file_metadata.ipynb`.


## How-to guides

How-to guides show how you can complete a specific task with your own data. You can start working through them in order if you like. You will have to combine different aspects of variaous how-to-guides in order to make a contribution.

The how-to guides include:

- `docs/guides/0.Prerequisites-EarthCODE-Workspaces.ipynb` - how to setup the enviroment to run the rest of the notebooks and commit the results locally.
- `docs/guides/Prerequisites-EarthCODE-Workspaces.ipynb` - how to setup the enviroment to run the rest of the notebooks and commit the results, using the EarthCODE workspace.
- `docs/guides/1.Project.ipynb` create and validate project metadata.
- `docs/guides/2.Product.ipynb` create and validate product metadata.
- `docs/guides/3.Workflow.ipynb` create and validate workflow metadata.
- `docs/guides/4.Experiment.ipynb` create and validate experiment metadata.
- `docs/guides/2.1.Product_files_PRR.ipynb` to show how to add a seperate catalog to a product.
- `docs/guides/2.1.Product_files_self_hosted.ipynb.ipynb` how to add files that already have stable public URLs.
- `docs/guides/5.Templates.ipynb` if you prefer the YAML-template workflow.


## Next steps

Start contributing by :
1. Creating a local or remote enviroment
2. Creating your own script or jupyter notebook to generate the metadata for your project, products, data files
3. Opening a PR against the Open Science Catalog, to start the review process. OR email the earthcode team for support