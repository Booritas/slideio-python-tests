import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np
import json
import cv2 as cv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity

class TestOMETiff(unittest.TestCase):


    def test_fluorescente_slide(self):
        file_path = Tools().getImageFilePath("ometiff", "Subresolutions/retina_large.ome.tiff", ImageDir.FULL)
        test_file_scene1 = Tools().getImageFilePath("ometiff", "Tests/retina_large.ome.tiff - retina_large.ims Resolution Level 1 (1, x=651, y=724, w=304, h=196).tif", ImageDir.FULL)
        with slideio.open_slide(file_path, 'OMETIFF') as slide:
            self.assertEqual(slide.num_scenes, 2)
            with slide.get_scene_by_name("retina_large.ims Resolution Level 1") as scene:
                self.assertEqual(scene.num_zoom_levels, 3)
                self.assertEqual(scene.rect, (0, 0, 2048, 1567))
                self.assertEqual(scene.magnification, 0)
                self.assertEqual(scene.num_channels, 2)
                self.assertEqual(scene.num_z_slices, 64)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.resolution, (2.2905761973056524e-08,2.2898531953649078e-08))
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.compression, slideio.Compression.Zlib)
                self.assertAlmostEqual(scene.z_resolution, 0.2e-6)
                scene_width, scene_height = scene.size
                self.assertEqual(scene_width, 2048)
                self.assertEqual(scene_height, 1567)
                block_rect = (651, 724, 304, 196)
                block = scene.read_block(block_rect, slices=(32, 33), channel_indices=[0])
                self.assertEqual(block.shape, (block_rect[3], block_rect[2]))
                reference_raster = cv.imread(test_file_scene1, cv.IMREAD_GRAYSCALE)
                self.assertEqual(block.shape, reference_raster.shape)
                self.assertTrue(np.array_equal(block, reference_raster))
            with slide.get_scene_by_name("retina_large.ims Resolution Level 2") as scene:
                self.assertEqual(scene.num_zoom_levels, 1)
                self.assertEqual(scene.rect, (0, 0, 256, 195))
                self.assertEqual(scene.magnification, 0)
                self.assertEqual(scene.num_channels, 2)
                self.assertEqual(scene.num_z_slices, 32)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.resolution, (1.8324609578445219e-07,1.8401025627165894e-07))
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.compression, slideio.Compression.Zlib)

    def test_rgb_slide(self):
        file_path = Tools().getImageFilePath("ometiff", "Subresolutions/Leica-1.ome.tiff", ImageDir.FULL)
        test_file = Tools().getImageFilePath("ometiff", "Tests/Leica-1.ome.tiff - Series 1 (1, x=21504, y=15360, w=512, h=512).png", ImageDir.FULL)
        slideio.open_slide(file_path, 'OMETIFF')
        with slideio.open_slide(file_path, 'OMETIFF') as slide:
            self.assertEqual(slide.num_scenes, 2)
            with slide.get_scene_by_name("Image:1") as scene:
                self.assertEqual(scene.rect, (0,0,36832, 38432))
                self.assertEqual(scene.size, (36832, 38432))
                self.assertEqual(scene.magnification, 20)
                self.assertEqual(scene.resolution, (0.5e-6, 0.5e-6))
                block_rect = ( 21504, 15360, 512, 512)
                block_raster = scene.read_block(block_rect, channel_indices=[0, 1, 2])
                image = Image.open(test_file)
                reference_raster = np.array(image)
                self.assertEqual(block_raster.shape, reference_raster.shape)
                sim = compute_similarity(block_raster, reference_raster)
                self.assertGreater(sim, 0.99, "Images are not similar enough")
                
    def test_multifile_slide(self):
        file_path = Tools().getImageFilePath("ometiff", "Multifile2/multifile-Z5.ome.tiff", ImageDir.FULL)
        test_file = Tools().getImageFilePath("ometiff", "Multifile2/multifile-Z3.ome.tiff", ImageDir.FULL)
        slideio.open_slide(file_path, 'OMETIFF')
        with slideio.open_slide(file_path, 'OMETIFF') as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,18, 24))
                self.assertEqual(scene.size, (18, 24))
                self.assertEqual(scene.magnification, 0)
                self.assertEqual(scene.resolution, (1.e-6, 1.e-6))
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.num_z_slices, 5)
                block_rect = (0, 0, 18, 24)
                block_raster = scene.read_block(block_rect, slices=(1, 4))
                self.assertEqual(block_raster.shape, (3,24,18))
                block_raster = scene.read_block(block_rect, slices=(2, 3))
                self.assertEqual(block_raster.shape, (24,18))
                image = Image.open(test_file)
                reference_raster = np.array(image)
                sim = compute_similarity(block_raster, reference_raster)
                self.assertGreater(sim, 0.9999, "Images are not similar enough")

    def test_large_slide(self):
        file_path = Tools().getImageFilePath("ometiff", "private/test.ome.tif", ImageDir.FULL)
        test_file1 = Tools().getImageFilePath("ometiff", "Tests/test.ome.tif - (1, x=12183, y=19915, w=402, h=274).tif", ImageDir.FULL)
        test_file2 = Tools().getImageFilePath("ometiff", "Tests/test.ome.tif - (2, x=12183, y=19915, w=402, h=274).tif", ImageDir.FULL)
        slideio.open_slide(file_path, 'OMETIFF')
        with slideio.open_slide(file_path, 'OMETIFF') as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,27136, 36160))
                self.assertEqual(scene.size, (27136, 36160))
                self.assertEqual(scene.magnification, 0)
                self.assertEqual(scene.resolution, (0.3262e-6, 0.3262e-6))
                self.assertEqual(scene.num_channels, 15)
                self.assertEqual(scene.num_z_slices, 1)
                block_rect = (12183, 19915, 402, 274)
                block_raster = scene.read_block(block_rect, channel_indices=[0])
                image = Image.open(test_file1)
                reference_raster = np.array(image)
                sim = compute_similarity(block_raster, reference_raster)
                self.assertGreater(sim, 0.9999, "Images are not similar enough")
        
if __name__ == '__main__':
    unittest.main()