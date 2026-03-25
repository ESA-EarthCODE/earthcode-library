from datetime import datetime

import pytest
from pystac.validation import RegisteredValidator

from earthcode.metadata_input_definitions import (
    ProductCollectionMetadata,
    ProjectCollectionMetadata,
    WorkflowMetadata,
    ExperimentMetadata,
    ItemMetadata
)
from earthcode.static import (
    create_product_collection,
    create_project_collection,
    create_workflow_record,
    create_experiment_record,
    generate_OSC_dummy_entries,
    create_item
)


expected_project =  {
  "type": "Collection",
  "id": "4datlantic-ohc",
  "stac_version": "1.0.0",
  "description": "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach.",
  "links": [
    {
      "rel": "root",
      "href": "../../catalog.json",
      "type": "application/json",
      "title": "Open Science Catalog"
    },
    {
      "rel": "parent",
      "href": "../catalog.json",
      "type": "application/json",
      "title": "Projects"
    },
    {
      "rel": "via",
      "href": "https://www.4datlantic-ohc.org/",
      "title": "Website"
    },
    {
      "rel": "via",
      "href": "https://eo4society.esa.int/projects/4datlantic-ohc/",
      "title": "EO4Society Link"
    },
    {
      "rel": "related",
      "href": "../../themes/oceans/catalog.json",
      "type": "application/json",
      "title": "Theme: Oceans"
    }
  ],
  "stac_extensions": [
    "https://stac-extensions.github.io/osc/v1.0.0/schema.json",
    "https://stac-extensions.github.io/themes/v1.0.0/schema.json",
    "https://stac-extensions.github.io/contacts/v0.1.1/schema.json"
  ],
  "osc:status": "completed",
  "osc:type": "project",
  "updated": "2025-12-18T16:34:51Z",
  "created": "2025-12-18T16:34:51Z",
  "themes": [
    {
      "scheme": "https://github.com/stac-extensions/osc#theme",
      "concepts": [
        {
          "id": "oceans"
        }
      ]
    }
  ],
  "contacts": [
    {
      "name": "Roberto Sabia",
      "roles": [
        "technical_officer"
      ],
      "emails": [
        {
          "value": "roberto.sabia@esa.int"
        }
      ]
    },
    {
      "name": "Magellium",
      "roles": [
        "consoritum_member"
      ],
      "emails": [
        {
          "value": "magellium.fr"
        }
      ]
    }
  ],
  "title": "4DAtlantic-OHC",
  "extent": {
    "spatial": {
      "bbox": [
        [
          -180.0,
          -90.0,
          180.0,
          90.0
        ]
      ]
    },
    "temporal": {
      "interval": [
        [
          "2021-07-06T00:00:00Z",
          "2025-06-12T00:00:00Z"
        ]
      ]
    }
  },
  "license": "proprietary"
}


### missions, variabnles and themes are different to the final product, 
# since an open science catalog instance is needed to find the final values
expected_product = {
  "type": "Collection",
  "id": "4d-atlantic-ohc-global",
  "stac_version": "1.0.0",
  "description": "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach. This dataset contains variables as 3D grids of ocean heat content anomalies at 1x1 resolution and monthly time step. Error variance-covariance matrices of OHC at regional scale and annual resolution are also provided. See Experimental Dataset Description for details: https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf. Version V3-0 of Dataset published 2025 in ODATIS-AVISO portal. This dataset has been produced within the framework of the 4DAtlantic-Ocean heat content Project funded by ESA.",
  "links": [
    {
      "rel": "root",
      "href": "../../catalog.json",
      "type": "application/json",
      "title": "Open Science Catalog"
    },
    {
      "rel": "parent",
      "href": "../catalog.json",
      "type": "application/json",
      "title": "Products"
    },
    {
      "rel": "related",
      "href": "../../projects/4datlantic-ohc/collection.json",
      "type": "application/json",
      "title": "Project: 4DAtlantic-OHC"
    },
  {'rel': 'related',
   'href': '../../eo-missions/in-situ-observations/catalog.json',
   'type': 'application/json',
   'title': 'Mission: In-situ-observations'},
  {'rel': 'related',
   'href': '../../eo-missions/grace-fo/catalog.json',
   'type': 'application/json',
   'title': 'Mission: Grace-fo'},
  {'rel': 'related',
   'href': '../../eo-missions/sentinel-6/catalog.json',
   'type': 'application/json',
   'title': 'Mission: Sentinel-6'},
  {'rel': 'related',
   'href': '../../eo-missions/jason-3/catalog.json',
   'type': 'application/json',
   'title': 'Mission: Jason-3'},
  {'rel': 'related',
   'href': '../../variables/ocean-heat-budget/catalog.json',
   'type': 'application/json',
   'title': 'Variable: Ocean Heat Budget'},
  {'rel': 'related',
   'href': '../../themes/oceans/catalog.json',
   'type': 'application/json',
   'title': 'Theme: Oceans'},
    {
      "rel": "via",
      "href": "https://opensciencedata.esa.int/stac-browser/#/external/https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
      "title": "Access"
    },
    {
      "rel": "via",
      "href": "https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf",
      "title": "Documentation"
    },
    {
      "rel": "child",
      "href": "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json",
      "title": "Global Ocean Heat Content"
    },
    {
      "rel": "license",
      "href": "https://www.aviso.altimetry.fr/fileadmin/documents/data/License_Aviso.pdf",
      "title": "License"
    }
  ],
  "stac_extensions": [
    "https://stac-extensions.github.io/osc/v1.0.0/schema.json",
    "https://stac-extensions.github.io/themes/v1.0.0/schema.json",
  ],
  "osc:project": "4datlantic-ohc",
  "osc:status": "completed",
  "osc:region": "Global",
  "osc:type": "product",
  "created": "2025-12-18T16:34:53Z",
  "updated": "2025-12-18T16:34:53Z",
  "themes": [
    {
      "scheme": "https://github.com/stac-extensions/osc#theme",
      "concepts": [
        {
          "id": "oceans"
        }
      ]
    }
  ],
  "osc:missions": [
    "in-situ-observations",
    "grace-fo",
    "sentinel-6",
    "jason-3"
  ],
  "osc:variables": [
    "ocean-heat-budget"
  ],
  "title": "Global Ocean Heat Content",
  "extent": {
    "spatial": {
      "bbox": [
        [
          -180.0,
          -90.0,
          180.0,
          90.0
        ]
      ]
    },
    "temporal": {
      "interval": [
        [
          "2021-01-01T00:00:00Z",
          "2021-12-31T00:00:00Z"
        ]
      ]
    }
  },
  "license": "other",
  "keywords": [
    "ocean",
    "heat",
    "content",
    "altimetry"
  ]
}


expected_workflow = {'id': '4datlantic-wf',
 'type': 'Feature',
 'geometry': None,
 'conformsTo': ['http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core'],
 'properties': {'title': '4D-Atlantic-Workflow',
  'description': 'This describes the OHC workflow',
  'type': 'workflow',
  'osc:project': '4datlantic-ohc',
  'osc:status': 'completed',
  'formats': [{'name': 'netcdf64'}],
  'updated': '2026-03-05T12:34:08Z',
  'created': '2026-03-05T12:34:08Z',
  'keywords': ['ocean', 'heat', 'çontent'],
  'license': 'CC-BYB4.0',
  'version': '1',
  'themes': [{'scheme': 'https://github.com/stac-extensions/osc#theme',
    'concepts': [{'id': 'oceans'}]}]},
 'linkTemplates': [],
 'links': [{'rel': 'root',
   'href': '../../catalog.json',
   'type': 'application/json',
   'title': 'Open Science Catalog'},
  {'rel': 'parent',
   'href': '../catalog.json',
   'type': 'application/json',
   'title': 'Workflows'},
  {'rel': 'related',
   'href': '../../projects/4datlantic-ohc/collection.json',
   'type': 'application/json',
   'title': 'Project: 4D Atlantic OHC'},
  {'rel': 'git',
   'href': 'https://github.com/ESA-EarthCODE/open-science-catalog-metadata',
   'type': 'application/json',
   'title': 'Git source repository'},
  {'rel': 'related',
   'href': '../../themes/oceans/catalog.json',
   'type': 'application/json',
   'title': 'Theme: Oceans'}]}

expected_experiment = {'id': '4datlantic-experiment',
 'type': 'Feature',
 'conformsTo': ['http://www.opengis.net/spec/ogcapi-records-1/1.0/req/record-core'],
 'geometry': None,
 'properties': {'created': '2026-03-05T12:39:28Z',
  'updated': '2026-03-05T12:39:28Z',
  'type': 'experiment',
  'title': '4D-Atlantic-Experiment',
  'description': 'This describes the OHC experiment',
  'keywords': ['ocean', 'heat', 'content'],
  'contacts': [{'name': 'EarthCODE Demo',
    'organization': 'EarthCODE',
    'links': [{'rel': 'about',
      'type': 'text/html',
      'href': 'https://opensciencedata.esa.int/'}],
    'contactInstructions': 'Contact via EarthCODE',
    'roles': ['host']}],
  'themes': [{'scheme': 'https://github.com/stac-extensions/osc#theme',
    'concepts': [{'id': 'oceans'}]}],
  'formats': [{'name': 'GeoTIFF'}],
  'license': 'CC-BY-SA-4.0',
  'osc:workflow': '4datlantic-wf'},
 'linkTemplates': [],
 'links': [{'rel': 'root',
   'href': '../../catalog.json',
   'type': 'application/json',
   'title': 'Open Science Catalog'},
  {'rel': 'parent',
   'href': '../catalog.json',
   'type': 'application/json',
   'title': 'Experiments'},
  {'rel': 'related',
   'href': '../../products/4datlantic-ohc/collection.json',
   'type': 'application/json',
   'title': 'Global Ocean Heat Content'},
  {'rel': 'related',
   'href': '../../workflows/4datlantic-wf/record.json',
   'type': 'application/json',
   'title': 'Workflow: 4D-Atlantic-Workflow'},
  {'rel': 'input',
   'href': 'https://github.com/deepesdl/cube-gen',
   'type': 'application/yaml',
   'title': 'Input parameters'},
  {'rel': 'environment',
   'href': 'https://github.com/deepesdl/cube-gen',
   'type': 'application/yaml',
   'title': 'Execution environment'},
  {'rel': 'related',
   'href': '../../themes/oceans/catalog.json',
   'type': 'application/json',
   'title': 'Theme: Oceans'}]}


def test_project_ohc():

    project_collection = create_project_collection(
        ProjectCollectionMetadata(
            project_id="4datlantic-ohc",
            project_title="4DAtlantic-OHC",
            project_description=(
                "Given the major role of the ocean in the climate system, it is essential to characterize "
                "the temporal and spatial variations of its heat content. The OHC product results from the "
                "space geodetic approach also called altimetry-gravimetry approach."
            ),
            project_status="completed",
            project_license="proprietary",
            project_bbox=[[-180.0, -90.0, 180.0, 90.0]],
            project_start_datetime=datetime(2021, 7, 6),
            project_end_datetime=datetime(2025, 6, 12),
            project_themes=["oceans"],
            to_name="Roberto Sabia",
            to_email="roberto.sabia@esa.int",
            consortium_members=[("Magellium", "magellium.fr")],
            website_link="https://www.4datlantic-ohc.org/",
            eo4society_link="https://eo4society.esa.int/projects/4datlantic-ohc/",
        )
    )

    # change updated and created dates
    project_dict = project_collection.to_dict()
    project_dict['created'] = "2025-12-18T16:34:51Z"
    project_dict['updated'] = "2025-12-18T16:34:51Z"

    assert project_dict == expected_project


def test_product_ohc():

    item_link = "https://s3.waw4-1.cloudferro.com/EarthCODE/Catalogs/4datlantic-ohc/collection.json"

    product_collection = create_product_collection(
        ProductCollectionMetadata(
            product_id="4d-atlantic-ohc-global",
            product_title="Global Ocean Heat Content",
            product_description=(
                "Given the major role of the ocean in the climate system, it is essential to characterize the temporal and spatial variations of its heat content. The OHC product results from the space geodetic approach also called altimetry-gravimetry approach. This dataset contains variables as 3D grids of ocean heat content anomalies at 1x1 resolution and monthly time step. Error variance-covariance matrices of OHC at regional scale and annual resolution are also provided. See Experimental Dataset Description for details: https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf. Version V3-0 of Dataset published 2025 in ODATIS-AVISO portal. This dataset has been produced within the framework of the 4DAtlantic-Ocean heat content Project funded by ESA."
            ),
            product_bbox=[[-180.0, -90.0, 180.0, 90.0]],
            product_start_datetime=datetime(2021, 1, 1),
            product_end_datetime=datetime(2021, 12, 31),
            product_license="other",
            product_keywords=["ocean", "heat", "content", "altimetry"],
            product_status="completed",
            product_region="Global",
            product_themes=["oceans"],
            product_missions=[ "in-situ-observations", "grace-fo", "sentinel-6", "jason-3"],
            product_variables=["ocean-heat-budget"],
            project_id="4datlantic-ohc",
            project_title="4DAtlantic-OHC",
            access_link=f"https://opensciencedata.esa.int/stac-browser/#/external/{item_link}",
            documentation_link=(
                "https://www.aviso.altimetry.fr/fileadmin/documents/data/tools/OHC-EEI/OHCATL-DT-035-MAG_EDD_V3.0.pdf"
            ),
            license_link='https://www.aviso.altimetry.fr/fileadmin/documents/data/License_Aviso.pdf',
            item_link=item_link,
            item_title="Global Ocean Heat Content"
        )
    )

    # change updated and created dates
    product_dict = product_collection.to_dict()
    product_dict['created'] = "2025-12-18T16:34:53Z"
    product_dict['updated'] = "2025-12-18T16:34:53Z"

    assert product_dict == expected_product

    # product_collection.validate()


def test_workflow_ohc():
    
    workflow_collection = create_workflow_record(
        WorkflowMetadata(
            workflow_id="4datlantic-wf",
            workflow_title="4D-Atlantic-Workflow",
            workflow_description="This describes the OHC workflow",
            workflow_license="CC-BYB4.0",
            workflow_keywords=["ocean", "heat", "çontent"],
            workflow_formats=["netcdf64"],
            workflow_themes=["oceans"],
            codeurl="https://github.com/ESA-EarthCODE/open-science-catalog-metadata",
            project_id="4datlantic-ohc",
            project_title="4D Atlantic OHC",
        )
    )
    workflow_collection['properties']['created'] = '2026-03-05T12:34:08Z'
    workflow_collection['properties']['updated'] = '2026-03-05T12:34:08Z'
    assert workflow_collection == expected_workflow

def test_experiment_ohc():
  workflow_id = "4datlantic-wf"
  workflow_title = "4D-Atlantic-Workflow"
  product_id = "4datlantic-ohc"

  experiment = create_experiment_record(
          ExperimentMetadata(
              experiment_id="4datlantic-experiment",
              experiment_title="4D-Atlantic-Experiment",
              experiment_description="This describes the OHC experiment",
              experiment_license="CC-BY-SA-4.0",
              experiment_keywords=["ocean", "heat", "content"],
              experiment_formats=["GeoTIFF"],
              experiment_themes=["oceans"],
              experiment_input_parameters_link="https://github.com/deepesdl/cube-gen",
              experiment_enviroment_link="https://github.com/deepesdl/cube-gen",
              workflow_id=workflow_id,
              workflow_title=workflow_title,
              product_id=product_id,
              product_title="Global Ocean Heat Content",
          )
      )
  experiment['properties']['created'] = '2026-03-05T12:39:28Z'
  experiment['properties']['updated'] = '2026-03-05T12:39:28Z'
  assert experiment == expected_experiment



def test_generate_dummy():
    project, product, workflow, experiment = generate_OSC_dummy_entries()
    assert project.id.endswith("+123")
    assert product.id.endswith("+123")
    assert workflow["id"].endswith("+123")
    assert experiment["id"].endswith("+123")
 
def test_item_creation():

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


  item = create_item(item_instance)

  ## aserts
  assert item.id == itemid
  assert item.geometry == geometry
  assert item.bbox == bbox
  assert item.datetime == data_time.to_pydatetime()
  assert item.collection_id == product_id
  assert item.properties.get("license") == item_license
  assert item.properties.get("description") == description
  assert "data" in item.assets
  assert item.assets["data"].href == data_url
  assert item.assets["data"].media_type == data_mime_type
  assert item.assets['data'].extra_fields["file:size"] == extra_fields["file:size"]
  assert item.assets['data'].extra_fields["file:compression"] == extra_fields["file:compression"]
  assert item.assets['data'].extra_fields["data:format"] == extra_fields["data:format"]