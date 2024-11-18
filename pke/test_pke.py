import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir

class TestVsi(unittest.TestCase):

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


        
if __name__ == '__main__':
    unittest.main()