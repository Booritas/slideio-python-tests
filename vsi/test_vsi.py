import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.test_tools import Tools, ImageDir

class TestVsi(unittest.TestCase):

    def test_vsi_rgb_slide(self):
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
            with slide.get_aux_image(aux_image_names[0]) as aux_image:
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

    def test_vsi_j2k_slide(self):
        file_path = Tools().getImageFilePath("vsi", "vsi-multifile/vsi-ets-test-jpg2k.vsi", ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_name = f"{file_name}_1.png"
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            num_scenes = slide.num_scenes
            self.assertEqual(1, num_scenes)
            self.assertEqual(0, slide.num_aux_images)
            aux_image_names = slide.get_aux_image_names()
            self.assertEqual(0, len(aux_image_names))
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,1645,1682))
                self.assertEqual(scene.origin, (0,0))
                self.assertEqual(scene.size, (1645,1682))
                self.assertEqual(scene.num_channels, 2)
                self.assertEqual(scene.num_z_slices, 11)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint16)
                self.assertEqual(scene.get_channel_data_type(1), np.uint16)
                self.assertEqual(scene.magnification, 60)
                self.assertAlmostEqual(scene.resolution[0], 0.1083e-6, 9)
                self.assertAlmostEqual(scene.resolution[1], 0.1083e-6, 9)
                self.assertEqual(scene.compression, slideio.Compression.Jpeg2000)
                slice = scene.read_block(channel_indices=[1], slices=(5,6))
                slice8b = slice/(np.max(slice)/255)
                image = Image.fromarray(slice8b.astype(np.uint8))
                image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(image, test_data))
            

        
if __name__ == '__main__':
    unittest.main()