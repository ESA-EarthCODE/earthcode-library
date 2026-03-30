import os
from datetime import datetime
import logging
import sys

import pystac
import yaml

from earthcode.static import create_project_collection, ProjectCollectionMetadata

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def create_project_stac_from_template(project_yaml, target):
    with open(project_yaml, 'r') as file:
        data = yaml.safe_load(file)

        for k, v in data.items():
            if v is None:
                log.error(f"The Project YAML contains an empty value for the following field: {k}")
                raise Exception(f"The Project YAML contains an empty value for the following field: {k}")

        # read spatial and temporal extent
        spatial_extent = pystac.SpatialExtent(data['extent']['spatial']['bbox']).bboxes
        temporal_start = datetime.strptime(data['extent']['temporal']['start'], "%Y-%m-%dT%H:%M:%SZ")
        temporal_end = datetime.strptime(data['extent']['temporal']['end'], "%Y-%m-%dT%H:%M:%SZ")

        # read consortium contacts
        project_cms = []
        [project_cms.append((member['name'], member['email'])) for member in data['consortium_members']]

    collection = create_project_collection(
        ProjectCollectionMetadata(
            project_id=data['id'] ,
            project_title=data['title'],
            project_description=data['description'],
            project_status=data['status'],
            project_license=data['license'],
            project_bbox=spatial_extent,
            project_start_datetime=temporal_start,
            project_end_datetime=temporal_end,
            project_themes=data['themes'],
            to_name=data['to_name'],
            to_email=data['to_email'],
            consortium_members=project_cms,
            website_link=data['link_website'],
            eo4society_link=data['link_eo4society']
        )
    )

    # save this file and copy it to the catalog/projects/{project}/collection.json
    collection.save_object(dest_href=os.path.join(target, 'project_collection.json'))
