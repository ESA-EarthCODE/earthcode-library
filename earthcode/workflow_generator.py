import os
import json
from datetime import datetime
import logging
import sys

import yaml

from earthcode.static import create_workflow_record, WorkflowMetadata

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def create_workflow_stac_from_template(project_yaml, target):
    with open(project_yaml, 'r') as file:
        data = yaml.safe_load(file)

        for k, v in data.items():
            if v is None:
                log.error(f"The Project YAML contains an empty value for the following field: {k}")
                raise Exception(f"The Project YAML contains an empty value for the following field: {k}")

        # read optional spatial and temporal extent
        spatial_extent = data.get('spatial_extent', None)
        temporal_extent = data.get('temporal_extent', None)
        if temporal_extent is not None:
            temporal_start = datetime.strptime(temporal_extent['start'], "%Y-%m-%dT%H:%M:%SZ")
            temporal_end = datetime.strptime(temporal_extent['end'], "%Y-%m-%dT%H:%M:%SZ")
        else:
            temporal_start = temporal_end = None

    workflow_metadata = WorkflowMetadata(
        workflow_id=data['id'],
        workflow_title=data['title'],
        workflow_description=data['description'],
        workflow_license=data['license'],
        workflow_keywords=data['keywords'],
        workflow_formats=data['formats'],
        workflow_themes=data['themes'],
        codeurl=data['link_code'],
        project_id=data['project'],
        project_title=data['project-title'],
        workflow_doi=data['sci:doi'],
        workflow_bbox=spatial_extent,
        workflow_start_datetime=temporal_start,
        workflow_end_datetime=temporal_end
    )

    workflow_record = create_workflow_record(workflow_metadata)

    # save this file and copy it to the catalog/workflows/{workflow-id}/record.json
    with open(os.path.join(target, 'workflow_record.json'), 'w') as f:
        json.dump(workflow_record, f, indent=2)
