import os
from datetime import datetime
import sys
import logging

import pystac
import yaml

from earthcode.static import create_product_collection, ProductCollectionMetadata

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def create_product_stac_from_template(project_yaml, target):
    with (open(project_yaml, 'r') as file):
        data = yaml.safe_load(file)

        for k, v in data.items():
            if v is None:
                log.error(f"The Project YAML contains an empty value for the following field: {k}")
                raise Exception(f"The Project YAML contains an empty value for the following field: {k}")

        # Define spatial and temporal extent
        spatial_extent = pystac.SpatialExtent(data['extent']['spatial']['bbox']).bboxes
        temporal_start = datetime.strptime(data['extent']['temporal']['start'], "%Y-%m-%dT%H:%M:%SZ")
        temporal_end = datetime.strptime(data['extent']['temporal']['end'], "%Y-%m-%dT%H:%M:%SZ")

        # optional
        product_license = data['license']
        if product_license == 'other':
            product_license_link = data['license_link']
        else:
            product_license_link = None

    product_metadata = ProductCollectionMetadata(
        product_id=data['id'],
        product_title=data['title'],
        product_description=data['description'],
        product_keywords=data['keywords'],
        product_status=data['status'],
        product_region=data['region'],
        product_themes=data['themes'],
        product_missions=data['missions'],
        product_variables=data['variables'],
        project_id=data['project'],
        project_title=data['project-title'],
        product_parameters=data['cf_parameters'],
        product_doi=data['sci:doi'],
        product_bbox=spatial_extent,
        product_start_datetime=temporal_start,
        product_end_datetime=temporal_end,
        product_license=product_license,
        license_link=product_license_link,
    )

    product_collection = create_product_collection(product_metadata)

    # save this file and copy it to the catalog/products/{product_id}/collection.json
    product_collection.save_object(dest_href=os.path.join(target, 'product_collection.json'))
