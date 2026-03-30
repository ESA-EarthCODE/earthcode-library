import argparse
import os
import shutil
from importlib import resources

from earthcode import project_generator, product_generator, workflow_generator, experiment_generator
import logging
import sys

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()


def generate_stac(project=None, workflow=None, experiment=None, product=None, target=os.getcwd()):
    """
    Generates the requested STAC json files at the desired target directory.
    If the folder does not exist it will be created.
    If no folder is specified the PWD where the program is run will be selected.

    :param project: Path to the Project YAML template, if empty no Project STAC will be generated
    :param workflow: Path to the Workflow YAML template, if empty no Workflow STAC will be generated
    :param experiment: Path to the Experiment YAML template, if empty no Experiment STAC will be generated
    :param product: Path to the Product YAML template, if empty no Product STAC will be generated
    :param target: target directory where the STAC json will be created.
    """
    if target is None:
        log.warning("No target folder specified, the STAC jsons will be generated in the PWD")
        target = os.getcwd()

    # Create target directory if it doesn't exist
    if not os.path.isdir(target):
        os.makedirs(target, exist_ok=True)

    if project is not None:
        log.info("Generating Project STAC json at \"" + target + "\"")
        project_generator.create_project_stac_from_template(project, target)
    if workflow is not None:
        log.info("Generating Workflow STAC json at \"" + target + "\"")
        workflow_generator.create_workflow_stac_from_template(workflow, target)
    if experiment is not None:
        log.info("Generating Experiment STAC json and relative YAML files at \"" + target + "\"")
        experiment_generator.create_experiment_stac_from_template(experiment, target)
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("experiment_environment.yaml")) as path:
            shutil.copy(path, target)
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("experiment_input.yaml")) as path:
            shutil.copy(path, target)
    if product is not None:
        log.info("Generating Product STAC json at \"" + target + "\"")
        product_generator.create_product_stac_from_template(product, target)

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
    parser.add_argument("-t", "--target", type=str,
                        help="The target location where the STAC jsons will be created.")

    args = parser.parse_args()

    generate_stac(args.project, args.workflow, args.experiment, args.product, args.target)


if __name__ == "__main__":
    main()
