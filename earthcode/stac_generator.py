import argparse
import os

from earthcode import project_generator, product_generator, workflow_generator, experiment_generator
import logging
import sys

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def generate_stac(osc_path, project=None, workflow=None, experiment=None, product=None):
    """
    Generates the requested STAC json files at the specified OSC repo.

    :param osc_path: OSC repo where the STAC json will be created.
    :param project: Path to the Project YAML template, if empty no Project STAC will be generated
    :param workflow: Path to the Workflow YAML template, if empty no Workflow STAC will be generated
    :param experiment: Path to the Experiment YAML template, if empty no Experiment STAC will be generated
    :param product: Path to the Product YAML template, if empty no Product STAC will be generated
    """

    if project is not None:
        log.info("Generating Project STAC json in OSC @ \"" + osc_path + "\"")
        project_generator.create_project_stac_from_template(project, osc_path)
    if workflow is not None:
        log.info("Generating Workflow STAC json in OSC @ \"" + osc_path + "\"")
        workflow_generator.create_workflow_stac_from_template(workflow, osc_path)
    if experiment is not None:
        log.info("Generating Experiment STAC json in OSC @ \"" + osc_path + "\"")
        experiment_generator.create_experiment_stac_from_template(experiment, osc_path)
    if product is not None:
        log.info("Generating Product STAC json in OSC @ \"" + osc_path + "\"")
        product_generator.create_product_stac_from_template(product, osc_path)

    if project is None and workflow is None and experiment is None and product is None:
        log.warning("No template provided."
                    "Run again with at least a provided template to produce the relative STAC json."
                    "For additional help invoke with -h.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", type=str,
                        help="Project YAML template location")
    parser.add_argument("-w", "--workflow", type=str,
                        help="Workflow YAML template location")
    parser.add_argument("-e", "--experiment", type=str,
                        help="Experiment YAML template location")
    parser.add_argument("-o", "--product", type=str,
                        help="Product YAML template location")
    parser.add_argument("-m", "--oscm", type=str,
                        help="The target OSC location where the STAC jsons will be created.")

    args = parser.parse_args()

    generate_stac(args.oscm, args.project, args.workflow, args.experiment, args.product)


if __name__ == "__main__":
    main()
