import unittest
import tempfile
import shutil
import os
import filecmp
from importlib import resources

from earthcode.template_generator import generate_template
from test_utils import assertIsFile


def assertIsFile(path):
    if not pathlib.Path(path).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(path))


class TestTemplateGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_generate_template(self):
        generate_template(project=True, workflow=True, experiment=True, product=True, target=self.test_dir)

        project = os.path.join(self.test_dir, "project.yaml")
        workflow = os.path.join(self.test_dir, "workflow.yaml")
        experiment = os.path.join(self.test_dir, "experiment.yaml")
        product = os.path.join(self.test_dir, "product.yaml")

        assertIsFile(project)
        assertIsFile(workflow)
        assertIsFile(experiment)
        assertIsFile(product)

        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("project.yaml")) as expected_project:
            self.assertTrue(filecmp.cmp(project, expected_project), "The project template is different from the expected one")

        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("workflow.yaml")) as expected_workflow:
            self.assertTrue(filecmp.cmp(workflow, expected_workflow), "The workflow template is different from the expected one")

        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("experiment.yaml")) as expected_experiment:
            self.assertTrue(filecmp.cmp(experiment, expected_experiment), "The experiment template is different from the expected one")

        with resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("product.yaml")) as expected_product:
            self.assertTrue(filecmp.cmp(product, expected_product), "The product template is different from the expected one")

    def test_generate_template_with_no_template_selected(self):
        with self.assertLogs(level='WARNING') as log:
            generate_template(project=False, workflow=False, experiment=False, product=False, target=self.test_dir)
            self.assertIn("No options selected.", log.output[0])
