"""slideio ZVI driver testing."""

import unittest
import pytest
import numpy as np
import slideio
import sys, os
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compare_images, compute_similarity


class TestNDPI(unittest.TestCase):
    """Tests for slideio NDPI driver functionality."""

    def test_openFile(self):
        """
        Open NDPI file

        """
        image_path =Tools().getImageFilePath("hamamatsu", "2017-02-27 15.29.08.ndpi",ImageDir.FULL)
            
        with slideio.open_slide(image_path, "NDPI") as slide:
            self.assertTrue(slide is not None)
            self.assertEqual(slide.num_scenes, 1)
            self.assertEqual(slide.num_aux_images, 2)
            self.assertEqual(slide.get_aux_image_names(), ["macro", "map"])
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0, 0, 11520, 9984))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.resolution, (0.45255011992578178e-6, 0.45255011992578178e-6))
                self.assertEqual(20., scene.magnification)
                self.assertEqual(np.uint8, scene.get_channel_data_type(0))
                self.assertEqual(np.uint8, scene.get_channel_data_type(1))
                self.assertEqual(np.uint8, scene.get_channel_data_type(2))

    def test_readImageBlocks(self):
        filePath = Tools().getImageFilePath("hamamatsu", "openslide/CMU-1.ndpi", ImageDir.FULL)
        testFilePath1 = Tools().getImageFilePath("hamamatsu", "openslide/CMU-1-1.png", ImageDir.FULL)
        testFilePath2 = Tools().getImageFilePath("hamamatsu", "openslide/CMU-1_002.tif", ImageDir.FULL)
        with slideio.open_slide(filePath, "NDPI") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.resolution, (4.5641259698767688e-7, 4.5506257110352676e-7))
                self.assertEqual(scene.rect, (0, 0, 51200, 38144))
                self.assertEqual(20., scene.magnification)
                self.assertEqual(np.uint8, scene.get_channel_data_type(0))
                self.assertEqual(np.uint8, scene.get_channel_data_type(1))
                self.assertEqual(np.uint8, scene.get_channel_data_type(2))
                self.assertEqual(slideio.Compression.Jpeg, scene.compression)

                block_rect = scene.rect
                block_size = (400, 298)
                block_raster = scene.read_block(block_rect, block_size)
                #Image.fromarray(block_raster).show()
                test_image = Image.open(testFilePath1)
                #test_image.show()
                test_raster = np.array(test_image)[:,:,:3]
                similarity = compute_similarity(block_raster, test_raster)
                self.assertGreater(similarity, 0.99)

                block_rect= (2000, 20000, 8000, 6000)
                block_size = (800, 600)
                block_raster = scene.read_block(block_rect, block_size)
                #Image.fromarray(block_raster).show()
                test_image = Image.open(testFilePath2)
                test_image = test_image.resize((800, 600))
                #test_image.show()
                test_raster = np.array(test_image)[:,:,:3]
                similarity = compute_similarity(block_raster, test_raster)
                self.assertGreater(similarity, 0.9)

    def test_readAuxImages(self):
        filePath = Tools().getImageFilePath("hamamatsu", "2017-02-27 15.29.08.ndpi", ImageDir.FULL)
        testFilePath1 = Tools().getImageFilePath("hamamatsu", "2017-02-27 15.29.08.macro.png", ImageDir.FULL)
        testFilePath2 = Tools().getImageFilePath("hamamatsu", "2017-02-27 15.29.08.map.png", ImageDir.FULL)
        with slideio.open_slide(filePath, "NDPI") as slide:
            num_aux_images = slide.num_aux_images
            self.assertEqual(num_aux_images, 2)
            self.assertEqual(slide.get_aux_image_names(), ["macro", "map"])

            macro = slide.get_aux_image("macro").read_block()
            macro_test = Image.open(testFilePath1)
            # Image.fromarray(macro).show()
            # macro_test.show()

            score = compute_similarity(macro, np.array(macro_test))
            self.assertGreater(score, 0.9999)

            map_test = Image.open(testFilePath2)
            map = slide.get_aux_image("map").read_block()
            score = compute_similarity(map, np.array(map_test))
            self.assertGreater(score, 0.9999)

    def test_readJpegXRImageBlocks(self):
        filePath = Tools().getImageFilePath("hamamatsu", "DM0014 - 2020-04-02 10.25.21.ndpi", ImageDir.FULL)
        testFilePath1 = Tools().getImageFilePath("hamamatsu", "DM0014 - 2020-04-02 10.25.21-roi-resampled.png", ImageDir.FULL)
        with slideio.open_slide(filePath, "NDPI") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.resolution, (4.4163759219184738e-07, 4.4163759219184738e-07))
                self.assertEqual(scene.rect, (0, 0, 69888, 34944))
                self.assertEqual(20., scene.magnification)
                self.assertEqual(np.uint16, scene.get_channel_data_type(0))
                self.assertEqual(slideio.Compression.JpegXR, scene.compression)

                rect = scene.rect
                coeff = 500./rect[2]
                block_size = (round(rect[2]*coeff),round(rect[3]*coeff))
                block_raster = scene.read_block(rect, block_size)
                #Image.fromarray(block_raster).show()
                test_image = Image.open(testFilePath1)
                #test_image.show()
                test_raster = np.array(test_image)
                similarity = compute_similarity(block_raster, test_raster)
                self.assertGreater(similarity, 0.99)

if __name__ == '__main__':
    unittest.main()
