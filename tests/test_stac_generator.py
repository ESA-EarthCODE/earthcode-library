import unittest
import tempfile
import shutil
import os
from importlib import resources

from earthcode.stac_generator import generate_stac
from test_utils import assertIsFile


class TestStacGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_generate_stac(self):
        with (resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("project.yaml")) as project_template,
              resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("workflow.yaml")) as workflow_template,
              resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("experiment.yaml")) as experiment_template,
              resources.as_file(resources.files("earthcode").joinpath("templates").joinpath("product.yaml")) as product_template):
            generate_stac(project=project_template, workflow=workflow_template, experiment=experiment_template, product=product_template, target=self.test_dir)

        project = os.path.join(self.test_dir, "project_collection.json")
        workflow = os.path.join(self.test_dir, "workflow_record.json")
        experiment = os.path.join(self.test_dir, "experiment_record.json")
        product = os.path.join(self.test_dir, "product_collection.json")

        assertIsFile(project)
        assertIsFile(workflow)
        assertIsFile(experiment)
        assertIsFile(product)

    def test_generate_template_with_no_template_selected(self):
        with self.assertLogs(level='WARNING') as log:
            generate_stac(project=None, workflow=None, experiment=None, product=None, target=self.test_dir)
            self.assertIn("No template provided.", log.output[0])
