"""slideio SCN driver testing."""
from PIL import Image
import unittest
import pytest
import cv2 as cv
import numpy as np
import slideio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity


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

    def test_3d_slide(self):
        image_path =Tools().getImageFilePath("scn", "private/HER2-63x_1.scn",ImageDir.FULL)
        test_image_path =Tools().getImageFilePath("scn", "private/page-67-StitchAB907A82-6319-422F-9B5B-EB0E0A9D0525-z=4-r=0-c=2.tiff",ImageDir.FULL)
        slide = slideio.open_slide(image_path, "SCN")
        self.assertEqual(slide.num_scenes, 7)
        self.assertEqual(slide.num_aux_images, 1)
        image_names = slide.get_aux_image_names()
        # self.assertTrue("Macro" in image_names)
        # self.assertTrue("Macro~1" in image_names)
        scene_found = False
        for scene_index in range(slide.num_scenes):
            scene = slide.get_scene(scene_index)
            if scene.name == "StitchAB907A82-6319-422F-9B5B-EB0E0A9D0525":
                self.assertEqual(scene.rect,(45655, 216712, 2573, 2674))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.get_channel_name(0), "DAPI")
                self.assertEqual(scene.get_channel_name(1), "Green #1")
                self.assertEqual(scene.get_channel_name(2), "Orange")
                self.assertEqual(scene.magnification, 63)
                self.assertAlmostEqual(scene.resolution[0], 1.028115040808395e-07, 10)
                self.assertAlmostEqual(scene.resolution[1], 1.0259237097980555e-07, 10)
                rect = scene.rect
                block_rect = (0, 0, rect[2], rect[3])
                channels = [2]
                scene_raster = scene.read_block(block_rect, channel_indices=channels, slices=(4, 5))
                ref_image = Image.open(test_image_path)
                test_raster = np.array(ref_image)
                sim = compute_similarity(scene_raster, test_raster)
                self.assertGreater(sim, 0.99)
                block_rect = (rect[2] // 2, rect[3] // 2, rect[2] // 4, rect[3] // 4)
                block_size = (rect[2] // 8, rect[3] // 8)
                scene_raster = scene.read_block(block_rect, block_size, channel_indices=channels, slices=(4, 5))
                crop = (block_rect[0], block_rect[1], block_rect[0]+block_rect[2], block_rect[1]+block_rect[3])
                crop_ref = ref_image.crop(crop)
                resized_ref = crop_ref.resize(block_size, Image.Resampling.BILINEAR)
                test_raster = np.array(resized_ref)
                sim = compute_similarity(scene_raster, test_raster)
                self.assertGreater(sim, 0.99)
                
                scene_found = True
                break
        self.assertTrue(scene_found, "Scene with name 'StitchAB907A82-6319-422F-9B5B-EB0E0A9D0525' not found")
        

if __name__ == '__main__':
    unittest.main()
