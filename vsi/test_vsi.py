import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity

class TestVsi(unittest.TestCase):

    def test_vsi_rgb_slide(self):
        file_path = Tools().getImageFilePath("vsi", "OS-1/OS-1.vsi", ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_name = f"{file_name}_1.png"
        overview_test_file_name = f"{file_name}_overview.png"
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            # check metadata
            metadata = slide.raw_metadata
            json_metadata = json.loads(metadata)
            self.assertEqual(json_metadata['tag'],-2)
            self.assertEqual(json_metadata['name'], 'root')
            val = json_metadata['value']
            self.assertEqual(val[0]['tag'], 2000)
            # check scenes
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
                sim_score = compute_similarity(block, test_data)
                self.assertGreater(sim_score, 0.999)

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
                sim_score = compute_similarity(block, test_data)
                self.assertGreater(sim_score, 0.999)

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
                image = slice8b.astype(np.uint8)
                # image = Image.fromarray(slice8b.astype(np.uint8))
                # image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                print(test_data.shape)
                sim_score = compute_similarity(image, test_data)
                self.assertGreater(sim_score, 0.999)

    def test_single_vsi_file(self):
        file_path = Tools().getImageFilePath("vsi", 
            "Zenodo/Q6VM49JF/Figure-1-ultrasound-raw-data/SPECTRUM_#201_2016-06-14_Jiangtao Liu/1286FL9057GDF8RGDX257R2GLHZ.vsi",
            ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        test_file_name = f"{file_name}_1.png"
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            self.assertEqual(1, slide.num_scenes)   
            self.assertEqual(0, slide.num_aux_images)
            aux_image_names = slide.get_aux_image_names()
            self.assertEqual(0, len(aux_image_names))
            metadata = slide.raw_metadata
            self.assertEqual(metadata,'')
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,608,600))
                self.assertEqual(scene.origin, (0,0))
                self.assertEqual(scene.size, (608,600))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 0)
                self.assertAlmostEqual(scene.resolution[0], 0., 9)
                self.assertAlmostEqual(scene.resolution[1], 0., 9)
                self.assertEqual(scene.num_zoom_levels, 1)
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                raster = scene.read_block(channel_indices=[1])
                # image = Image.fromarray(raster)
                # image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(raster, test_data))
                metadata = slide.raw_metadata
                self.assertEqual(metadata,'')
            
    def test_multiple_ets_files(self):
        file_path = Tools().getImageFilePath("vsi", 
            "Zenodo/Abdominal/G1M16_ABD_HE_B6.vsi",
            ImageDir.FULL)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            # check metadata
            metadata = slide.raw_metadata
            json_metadata = json.loads(metadata)
            self.assertEqual(json_metadata['tag'],-2)
            self.assertEqual(json_metadata['name'], 'root')
            val = json_metadata['value']
            self.assertEqual(val[0]['tag'], 2000)
            # check scenes
            self.assertEqual(3, slide.num_scenes)   
            #self.assertEqual(0, slide.num_aux_images)
            aux_image_names = slide.get_aux_image_names()
            self.assertEqual(1, len(aux_image_names))
            self.assertEqual("Overview", aux_image_names[0])
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,14749,20874))
                self.assertEqual(scene.origin, (0,0))
                self.assertEqual(scene.size, (14749,20874))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 40)
                self.assertAlmostEqual(scene.resolution[0], 0.1722e-6, 9)
                self.assertAlmostEqual(scene.resolution[1], 0.1722e-6, 9)
                self.assertEqual(scene.num_zoom_levels, 7)
                magnification = scene.magnification
                for i in range(scene.num_zoom_levels):
                    zoomLevel = scene.get_zoom_level_info(i)
                    self.assertAlmostEqual(zoomLevel.magnification, magnification,1)
                    self.assertEqual(zoomLevel.tile_size.width, 512)
                    self.assertEqual(zoomLevel.tile_size.height, 512)
                    magnification /= 2
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
                scene_rect = scene.rect
                x = scene_rect[2]//2
                y = scene_rect[3]//2
                block_rect = (x,y,600,600)
                raster = scene.read_block(rect=block_rect, channel_indices=[0])
                test_file_name = f"{file_name}_0.png"
                # image = Image.fromarray(raster)
                # image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(raster, test_data))
            with slide.get_scene(1) as scene:
                self.assertEqual(scene.rect, (0,0,15596,19403))
                self.assertEqual(scene.origin, (0,0))
                self.assertEqual(scene.size, (15596,19403))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 40)
                self.assertAlmostEqual(scene.resolution[0], 0.1722e-6, 9)
                self.assertAlmostEqual(scene.resolution[1], 0.1722e-6, 9)
                self.assertEqual(scene.num_zoom_levels, 7)
                magnification = scene.magnification
                for i in range(scene.num_zoom_levels):
                    zoomLevel = scene.get_zoom_level_info(i)
                    self.assertAlmostEqual(zoomLevel.magnification, magnification,1)
                    self.assertEqual(zoomLevel.tile_size.width, 512)
                    self.assertEqual(zoomLevel.tile_size.height, 512)
                    magnification /= 2
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
                scene_rect = scene.rect
                x = scene_rect[2]//2
                y = scene_rect[3]//2
                block_rect = (x,y,600,600)
                raster = scene.read_block(rect=block_rect, channel_indices=[0,1,2])
                test_file_name = f"{file_name}_1.png"
                # image = Image.fromarray(raster)
                # image.save(Tools().getTestImagePath("vsi", test_file_name))
                test_image = Image.open(Tools().getTestImagePath("vsi", test_file_name))
                test_data = np.array(test_image)
                self.assertTrue(np.array_equal(raster, test_data))

    def test_invalid_scene(self):
        file_path = Tools().getImageFilePath("vsi", 
            "vs200-vsi-share/Image_B309.vsi",
            ImageDir.FULL)
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertIsNotNone(slide)
            # check metadata
            self.assertEqual(0, slide.num_scenes)   
            self.assertEqual(2, slide.num_aux_images)
            aux_image_names = slide.get_aux_image_names()
            self.assertEqual(2, len(aux_image_names))
            self.assertEqual("Macro image", aux_image_names[0])
            self.assertEqual("Overview", aux_image_names[1])
            with slide.get_aux_image(aux_image_names[1]) as scene:
                self.assertEqual(scene.rect, (0,0,18124,9196))
                self.assertEqual(scene.origin, (0,0))
                self.assertEqual(scene.size, (18124,9196))
                self.assertEqual(scene.num_channels, 3)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 2)
                self.assertAlmostEqual(scene.resolution[0], 2.7243e-6, 9)
                self.assertAlmostEqual(scene.resolution[1], 2.7241e-6, 9)
                self.assertEqual(scene.num_zoom_levels, 7)
                magnification = scene.magnification
                for i in range(scene.num_zoom_levels):
                    zoomLevel = scene.get_zoom_level_info(i)
                    self.assertAlmostEqual(zoomLevel.magnification, magnification,1)
                    self.assertEqual(zoomLevel.tile_size.width, 512)
                    self.assertEqual(zoomLevel.tile_size.height, 512)
                    magnification /= 2
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
        
    def test_voulmes(self):
        file_path = Tools().getImageFilePath("vsi", 
            "private/d/STS_G6889_11_1_pHH3.vsi",
            ImageDir.FULL)
        test_file_path = Tools().getImageFilePath("vsi", 
            "test-output/STS_G6889_11_1_pHH3.vsi - 40x_BF_01 (1, x=82570, y=77046, w=1153, h=797).png",
            ImageDir.FULL)
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertEqual(slide.num_scenes,1)
            self.assertEqual(slide.num_aux_images,2)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.num_channels,3)
                self.assertEqual(scene.num_z_slices,1)
                self.assertEqual(scene.num_t_frames,1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 40)
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
                block = scene.read_block(rect=(82570,77046,1153,797), channel_indices=[0,1,2])
                test_image = Image.open(test_file_path)
                test_data = np.array(test_image)
                similarity = compute_similarity(block, test_data)
                self.assertGreater(similarity, 0.99)
        
    def test_stack3d(self):
        file_path = Tools().getImageFilePath("vsi", 
            "private/3d/01072022_35_2_z.vsi",
            ImageDir.FULL)
        test_file_path = Tools().getImageFilePath("vsi", 
            "private/3d/test-images/01072022_35_2_z.vsi - 60x_BF_Z_01 (1, x=45625, y=42302, w=984, h=1015).png",
            ImageDir.FULL)
        with slideio.open_slide(file_path, "VSI") as slide:
            self.assertEqual(slide.num_scenes,1)
            self.assertEqual(slide.num_aux_images,2)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.num_channels,3)
                self.assertEqual(scene.num_z_slices,13)
                self.assertEqual(scene.num_t_frames,1)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)
                self.assertEqual(scene.get_channel_data_type(1), np.uint8)
                self.assertEqual(scene.get_channel_data_type(2), np.uint8)
                self.assertEqual(scene.magnification, 60)
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
                block = scene.read_block(rect=(45625,42302,984,1015), channel_indices=[0,1,2], slices=(6,7))
                test_image = Image.open(test_file_path)
                test_data = np.array(test_image)
                similarity = compute_similarity(block, test_data)
                # block_image = Image.fromarray(block)
                # block_image.show()
                # test_image.show()
                self.assertGreater(similarity, 0.99)

if __name__ == '__main__':
    unittest.main()