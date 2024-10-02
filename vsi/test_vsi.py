import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.test_tools import Tools, ImageDir

class TestVsi(unittest.TestCase):

    def test_vsi_open(self):
        file_path = Tools().getImageFilePath("vsi", "OS-1/OS-1.vsi", ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_name = f"{file_name}_1.png"
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(1, num_scenes)
            with slide.get_scene(0) as scene:
                scene_rect = (0,0,66982,76963)
                self.assertEqual(scene_rect, scene.rect)
                self.assertIsNotNone(scene)
                num_channels = scene.num_channels
                self.assertEqual(3, num_channels)
                #self.assertEqual(scene.magnification, 20.)
                x = scene_rect[2]//2
                y = scene_rect[3]//2
                block_rect = (x,y,600,600)
                block = scene.read_block(rect=block_rect, size=(300,300))
                image = Image.fromarray(block)
                #image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(block, test_data))

        
if __name__ == '__main__':
    unittest.main()