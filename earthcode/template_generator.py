import argparse
import os
import shutil
from importlib import resources

import logging
import sys

logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
log = logging.getLogger()

def generate_template(project=False, workflow=False, experiment=False, product=False, target=os.getcwd()):
    """
    Creates requested yaml templates at the desired target folder.
    If the folder does not exist it will be created.
    If no folder is specified the PWD where the program is run will be selected.

    :param project: If True: generates the Project yaml template
    :param workflow: If True: generates the Workflow yaml template
    :param experiment: If True: generates the Experiment yaml template
    :param product: If True: generates the Product yaml template
    :param target: target directory where the templates will be generated.
    """
    # If empty use PWD as target directory
    if target is None:
        log.warning("No target folder specified, the templates will be generated in the PWD")
        target = os.getcwd()

    # Create target directory if it doesn't exist
    if not os.path.isdir(target):
        os.makedirs(target, exist_ok=True)

    if project:
        log.info("Generating Project template at \""+target+"\"")
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("project.yaml")) as path:
            shutil.copy(path, target)

    if workflow:
        log.info("Generating Workflow template at \""+target+"\"")
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("workflow.yaml")) as path:
            shutil.copy(path, target)

    if experiment:
        log.info("Generating Experiment template at \""+target+"\"")
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("experiment.yaml")) as path:
            shutil.copy(path, target)

    if product:
        log.info("Generating Product template at \""+target+"\"")
        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("product.yaml")) as path:
            shutil.copy(path, target)

    if not project and not workflow and not experiment and not product:
        log.warning("No options selected."
                    "Run again with at least one option to produce the templates."
                    "For additional help invoke with -h")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", action='store_true',
                        help="If present generate a project template")
    parser.add_argument("-w", "--workflow", action='store_true',
                        help="If present generate a workflow template")
    parser.add_argument("-e", "--experiment", action='store_true',
                        help="If present generate an experiment template")
    parser.add_argument("-o", "--product", action='store_true',
                        help="If present generate a product template")
    parser.add_argument("-t", "--target", type=str,
                        help="The target location where the templates will be generated.")

    args = parser.parse_args()

    generate_template(args.project, args.workflow, args.experiment, args.product, args.target)


if __name__ == "__main__":
    main()
