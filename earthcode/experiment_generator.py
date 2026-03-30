import os
import json
from datetime import datetime
import logging
import sys

import yaml

from earthcode.static import create_experiment_record, ExperimentMetadata

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def create_experiment_stac_from_template(experiment_yaml, target):
    with open(experiment_yaml, 'r') as file:
        data = yaml.safe_load(file)

        for k, v in data.items():
            if v is None:
                log.error(f"The Project YAML contains an empty value for the following field: {k}")
                raise Exception(f"The Project YAML contains an empty value for the following field: {k}")

        temporal_extent = data.get('temporal_extent', None)
        if temporal_extent is not None:
            temporal_start = datetime.strptime(temporal_extent['start'], "%Y-%m-%dT%H:%M:%SZ")
            temporal_end = datetime.strptime(temporal_extent['end'], "%Y-%m-%dT%H:%M:%SZ")
        else:
            temporal_start = temporal_end = None

        experiment_metadata = ExperimentMetadata(
            experiment_id=data['id'],
            experiment_title=data['title'],
            experiment_description=data['description'],
            experiment_license=data['license'],
            experiment_keywords=data['keywords'],
            experiment_formats=data['formats'],
            experiment_themes=data['themes'],
            experiment_input_parameters_link=data['link_params'],
            experiment_enviroment_link=data['link_env'],
            workflow_id=data['workflow'],
            workflow_title=data['workflow-title'],
            product_id=data['product'],
            product_title=data['product-title'],
            contacts=data.get('contacts', None),
            experiment_bbox=data.get('spatial_extent', None),
            experiment_start_datetime=temporal_start,
            experiment_end_datetime=temporal_end,
        )

    experiment_record = create_experiment_record(experiment_metadata)

    # save this file and copy it to the catalog/experiments/{experiment-id}/record.json
    with open(os.path.join(target, 'experiment_record.json'), 'w') as f:
        json.dump(experiment_record, f, indent=2)
