"""slideio module core functionality testing."""

import unittest
import pytest
import slideio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir


class TestCore(unittest.TestCase):
    """Tests for core functionality of the slideio module."""

    def test_core_driver_list(self):
        """The test checks if all drivers are available."""
        driver_ids = slideio.get_driver_ids()
        self.assertTrue("SVS" in driver_ids)
        self.assertTrue("GDAL" in driver_ids)
        self.assertTrue("CZI" in driver_ids)

    def test_core_not_existing_driver(self):
        """
        Test for calling of not-existing driver.

        Checks if slideio throws RuntimeError
        exception during opening of not existing file.
        """
        image_path = Tools().getImageFilePath("vsi", "OS-1/OS-1.vsi", ImageDir.FULL)
        
        with pytest.raises(RuntimeError):
            slideio.open_slide(image_path, "AAAA")


if __name__ == '__main__':
    unittest.main()
