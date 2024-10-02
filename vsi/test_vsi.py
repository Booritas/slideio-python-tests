import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.test_tools import Tools, ImageDir

class TestVsi(unittest.TestCase):

    def test_vsi_slide(self):
        file_path = Tools().getImageFilePath("vsi", "OS-1/OS-1.vsi", ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_name = f"{file_name}_1.png"
        overview_test_file_name = f"{file_name}_overview.png"
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(1, num_scenes)
            aux_image_names = slide.get_aux_image_names()
            self.assertEqual(1, len(aux_image_names))
            self.assertEqual("Overview", aux_image_names[0])
            with slide.get_scene(0) as scene:
                scene_rect = (0,0,66982,76963)
                self.assertEqual(scene_rect, scene.rect)
                self.assertIsNotNone(scene)
                num_channels = scene.num_channels
                self.assertEqual(3, num_channels)
                self.assertEqual(scene.magnification, 20.)
                self.assertAlmostEqual(scene.resolution[0], 0.3461e-6, 9)
                self.assertAlmostEqual(scene.resolution[1], 0.3461e-6, 9)
                self.assertEqual(3, scene.num_channels)
                self.assertEqual(1, scene.num_z_slices)
                self.assertEqual(1, scene.num_t_frames)
                print(scene.get_channel_data_type(0))
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.num_zoom_levels, 9)
                magnification = scene.magnification
                for i in range(scene.num_zoom_levels):
                    zoomLevel = scene.get_zoom_level_info(i)
                    self.assertAlmostEqual(zoomLevel.magnification, magnification,1)
                    magnification /= 2

                zoomLevel = scene.get_zoom_level_info(0)
                x = scene_rect[2]//2
                y = scene_rect[3]//2
                block_rect = (x,y,600,600)
                block = scene.read_block(rect=block_rect, size=(300,300))
                #image = Image.fromarray(block)
                #image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(block, test_data))
            aux_image = slide.get_aux_image(aux_image_names[0])
            self.assertEqual(aux_image.rect, (0, 0, 6753, 13196))
            self.assertEqual(aux_image.num_channels, 3)
            self.assertEqual(aux_image.num_z_slices, 1)
            self.assertEqual(aux_image.num_t_frames, 1)
            self.assertEqual(aux_image.get_channel_data_type(0), np.uint8)
            self.assertEqual(aux_image.get_channel_data_type(1), np.uint8)
            self.assertEqual(aux_image.get_channel_data_type(2), np.uint8)
            self.assertEqual(aux_image.magnification, 2)
            self.assertAlmostEqual(aux_image.resolution[0], 3.488e-6, 8)
            self.assertAlmostEqual(aux_image.resolution[1], 3.4892e-6, 8)
            block_rect = aux_image.rect
            block = aux_image.read_block(rect=block_rect, size=(0,300))
            #image = Image.fromarray(block)
            #image.save(Tools().getTestImagePath("vsi", overview_test_file_name))
            test_image = Image.open(Tools().getTestImagePath("vsi", overview_test_file_name))
            test_data = np.array(test_image)
            self.assertTrue(np.array_equal(block, test_data))
            

        
if __name__ == '__main__':
    unittest.main()