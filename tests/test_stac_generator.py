import unittest
import tempfile
import shutil

from earthcode.generators.stac_generator import generate_stac


class TestStacGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_generate_template_with_no_template_selected(self):
        with self.assertLogs(level='WARNING') as log:
            generate_stac(project=None, workflow=None, experiment=None, product=None, osc_path=self.test_dir)
            self.assertIn("No template provided.", log.output[0])
