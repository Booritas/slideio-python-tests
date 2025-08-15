import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir

def print_channel_info(channel_index, channel):
    print(f"Channel {channel_index} info:")
    print(f"\tMinimum: {np.min(channel)}")
    print(f"\tMaximum: {np.max(channel)}")
    print(f"\tAverage: {np.mean(channel)}")

class TestPKE(unittest.TestCase):

    def test_multichannel_slide(self):
        file_path = Tools().getImageFilePath("pke", "openmicroscopy/PKI_scans/LuCa-7color_Scan1.qptiff", ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        ref_image_path = Tools().getTestImagePath("pke", f"{file_name}-1.png")
        with slideio.open_slide(file_path, "QPTIFF") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(num_scenes, 1)
            scene = slide.get_scene(0)
            num_channels = scene.num_channels
            self.assertEqual(num_channels, 5)
            rect = scene.rect
            size = (500, 0)
            region = scene.read_block(rect, size)
            # image = Image.fromarray(region)
            # image.save(ref_image_path)
            first_slice = region[:, :, 0]
            last__slice = region[:, :, 4]
            print("first_slice: ", np.max(first_slice))
            print("last__slice: ", np.max(last__slice))   
            self.assertFalse(np.array_equal(first_slice, last__slice))


    def test_multichannel_slide_no_scale_separate_channels(self):
        file_path = Tools().getImageFilePath("pke", "openmicroscopy/PKI_scans/LuCa-7color_Scan1.qptiff", ImageDir.FULL)
        file_name = "LuCa-7color_Scan1.qptiff - resolution #1 (1, x=11619, y=16875, w=1202, h=756).tif"
        ref_image_path = Tools().getTestImagePath("pke", file_name)
        ref_image = Image.open(ref_image_path)
        region_rect = (11619, 16875, 1202, 756)
        with slideio.open_slide(file_path, "QPTIFF") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(num_scenes, 1)
            with slide.get_scene(0) as scene:
                num_channels = scene.num_channels
                self.assertEqual(num_channels, 5)
                for channel_index in range(num_channels):
                    ref_image.seek(channel_index)
                    channel_raster = scene.read_block(region_rect, channel_indices=[channel_index])
                    ref_raster = np.array(ref_image)
                    self.assertTrue(np.array_equal(channel_raster, ref_raster))
                    
    def test_multichannel_slide_no_scale_all_channels(self):
        file_path = Tools().getImageFilePath("pke", "openmicroscopy/PKI_scans/LuCa-7color_Scan1.qptiff", ImageDir.FULL)
        file_name = "LuCa-7color_Scan1.qptiff - resolution #1 (1, x=11619, y=16875, w=1202, h=756).tif"
        ref_image_path = Tools().getTestImagePath("pke", file_name)
        ref_image = Image.open(ref_image_path)
        region_rect = (11619, 16875, 1202, 756)
        with slideio.open_slide(file_path, "QPTIFF") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(num_scenes, 1)
            with slide.get_scene(0) as scene:
                num_channels = scene.num_channels
                self.assertEqual(num_channels, 5)
                image_raster = scene.read_block(region_rect)
                for channel_index in range(num_channels):
                    ref_image.seek(channel_index)
                    ref_raster = np.array(ref_image)
                    channel_raster = image_raster[:, :, channel_index]
                    self.assertTrue(np.array_equal(channel_raster, ref_raster))

        
if __name__ == '__main__':
    unittest.main()