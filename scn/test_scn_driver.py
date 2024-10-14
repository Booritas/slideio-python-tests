"""slideio SCN driver testing."""

import unittest
import pytest
import cv2 as cv
import numpy as np
import slideio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir


class TestSCN(unittest.TestCase):
    """Tests for slideio SCN driver functionality."""

    def test_driver_available(self):
        """
        Check if the driver is available.
        """
        drivers = slideio.get_driver_ids()
        self.assertTrue("SCN" in drivers)
 
    def test_raw_metadata(self):
        image_path =Tools().getImageFilePath("scn", "Leica-Fluorescence-1.scn",ImageDir.PUBLIC)
        slide = slideio.open_slide(image_path, "SCN")
        mtd = slide.raw_metadata
        self.assertTrue(mtd.startswith("<?xml version="))

    def test_open_file(self):
        image_path =Tools().getImageFilePath("scn", "Leica-Fluorescence-1.scn",ImageDir.PUBLIC)
        slide = slideio.open_slide(image_path, "SCN")
        self.assertEqual(slide.num_scenes, 1)
        self.assertEqual(slide.num_aux_images, 2)
        image_names = slide.get_aux_image_names()
        self.assertTrue("Macro" in image_names)
        self.assertTrue("Macro~1" in image_names)
        scene = slide.get_scene(0)
        self.assertEqual(scene.rect,(16306, 40361, 4737, 6338))
        self.assertEqual(scene.num_channels, 3)
        self.assertEqual(scene.get_channel_name(0), "405|Empty")
        self.assertEqual(scene.get_channel_name(1), "L5|Empty")
        self.assertEqual(scene.get_channel_name(2), "TX2|Empty")
        self.assertEqual(scene.magnification, 20)
        self.assertAlmostEqual(scene.resolution[0], 0.5e-6, 10)
        self.assertAlmostEqual(scene.resolution[1], 0.5e-6, 10)


    def test_read_macro(self):
        ref_image_path = Tools().getTestImagePath("scn", "Leica-Fluorescence-1/thumbnail.png")
        ref_macro = cv.imread(ref_image_path, cv.IMREAD_UNCHANGED)
        width = ref_macro.shape[1]
        height = ref_macro.shape[0]
        image_path =Tools().getImageFilePath("scn", "Leica-Fluorescence-1.scn",ImageDir.PUBLIC)
        slide = slideio.open_slide(image_path, "SCN")
        macro = slide.get_aux_image_raster("Macro",size=(width,height), channel_indices=[2,1,0])
        self.assertTrue(np.array_equal(macro, ref_macro))
        

if __name__ == '__main__':
    unittest.main()
