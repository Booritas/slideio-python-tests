"""slideio ZVI driver testing."""

import unittest
import pytest
import cv2 as cv
import numpy as np
import slideio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compare_images


class TestZVI(unittest.TestCase):
    """Tests for slideio ZVI driver functionality."""

    def test_not_existing_file(self):
        """
        Opening of not existing image.

        Checks if slideio throws RuntimeError
        exception during opening of not existing file.
        """
        image_path = "missing_file.png"
        with pytest.raises(RuntimeError):
            slideio.open_slide(image_path, "ZVI")

    def test_readblock_emptyChannelIndices(self):
        """
        Read a 3D image block w/o setting of channel indices

        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Stacked.zvi",ImageDir.PUBLIC)
            
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            with slide.get_scene(0) as scene:
                # read channel block
                raster = scene.read_block(slices=(0,3))
                shape = raster.shape
                self.assertEqual(shape[0],3)
                self.assertEqual(shape[1],1040)
                self.assertEqual(shape[2],1388)
                self.assertEqual(shape[3],3)


    def test_open_slidei2D(self):
        """
        Open a 2D image and read metadata
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Merged.zvi",ImageDir.PUBLIC)

        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                rect = scene.rect
                self.assertEqual(rect, (0, 0, 1480, 1132))
                size = scene.size
                self.assertEqual(size,(1480, 1132))
                org = scene.origin
                self.assertEqual(org, (0, 0))
                channel_count = scene.num_channels
                self.assertEqual(channel_count, 3)
                name = scene.get_channel_name(0)
                self.assertEqual(name, 'Hoechst 33342')
                name = scene.get_channel_name(1)
                self.assertEqual(name, 'Cy3')
                name = scene.get_channel_name(2)
                self.assertEqual(name, 'FITC')
                name = scene.name
                self.assertEqual(name, 'RQ26033_04310292C0004S_Calu3_amplified_100x_21Jun2012 ic zsm.zvi')
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                self.assertEqual(scene.resolution, (0.0645e-6, 0.0645e-6))
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)


    def test_open_slidei3D(self):
        """
        Open a 3D image and read metadata
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Stacked.zvi",ImageDir.PUBLIC)
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                rect = scene.rect
                self.assertEqual(rect, (0, 0, 1388, 1040))
                size = scene.size
                self.assertEqual(size,(1388, 1040))
                org = scene.origin
                self.assertEqual(org, (0, 0))
                channel_count = scene.num_channels
                self.assertEqual(channel_count, 3)
                name = scene.get_channel_name(0)
                self.assertEqual(name, 'Hoechst 33342')
                name = scene.get_channel_name(1)
                self.assertEqual(name, 'Cy3')
                name = scene.get_channel_name(2)
                self.assertEqual(name, 'FITC')
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                self.assertEqual(scene.resolution, (0.0645e-6, 0.0645e-6))
                self.assertEqual(scene.z_resolution, 0.25e-6)
                self.assertEqual(scene.num_z_slices, 13)
                self.assertEqual(scene.num_t_frames, 1)


    def test_read_image(self):
        """
        Read 2D image
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Merged.zvi",ImageDir.PUBLIC)
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                channel_count = scene.num_channels
                image = scene.read_block()
                for channel_index in range(0, channel_count):
                    channel_raster = image[:,:,channel_index]
                    test_image_path = Tools().getTestImagePath("zvi", f"Zeiss-1-Merged-ch{channel_index}.tif")
                    test_raster = cv.imread(test_image_path, cv.IMREAD_UNCHANGED)
                    score = compare_images(channel_raster.copy(), test_raster)
                    self.assertEqual(score, 1)


    def test_read_image_block(self):
        """
        Read a block from 2D image
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Merged.zvi",ImageDir.PUBLIC)
        roi = (200, 300, 500, 600)
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                channel_count = scene.num_channels
                image = scene.read_block(rect=roi)
                for channel_index in range(0, channel_count):
                    channel_raster = image[:,:,channel_index]
                    test_image_path = Tools().getTestImagePath("zvi", f"Zeiss-1-Merged-ch{channel_index}.tif")
                    test_raster = cv.imread(test_image_path, cv.IMREAD_UNCHANGED)
                    test_raster_roi = test_raster[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
                    score = compare_images(channel_raster.copy(), test_raster_roi.copy())
                    self.assertEqual(score, 1)


    def test_read_image_slice(self):
        """
        Read a slice from 3D image
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Stacked.zvi",ImageDir.PUBLIC)
        raw_slice_path = Tools().getTestImagePath("zvi","Zeiss-1-Stacked/zvi_slice_5_channel_2")
        raw_slice = np.fromfile(raw_slice_path,dtype=np.short)
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                image = scene.read_block(channel_indices=(2,), slices=(5,6))
                size = scene.size
                raw_slice = np.reshape(raw_slice, (size[1],size[0]))
                score = compare_images(image, raw_slice)
                self.assertEqual(score, 1)


    def test_read_3d_roi(self):
        """
        Read 3D roi from 3D image
        """
        image_path =Tools().getImageFilePath("zvi","Zeiss-1-Stacked.zvi",ImageDir.PUBLIC)
        raw_slice_path = Tools().getTestImagePath("zvi","Zeiss-1-Stacked/zvi_slice_5_channel_2")
        raw_slice = np.fromfile(raw_slice_path,dtype=np.short)
        roi = (200, 300, 500, 600)
        with slideio.open_slide(image_path, "ZVI") as slide:
            self.assertTrue(slide is not None)
            scene_count = slide.num_scenes
            self.assertEqual(scene_count, 1)
            with slide.get_scene(0) as scene:
                image = scene.read_block(rect=roi, channel_indices=(1,2), slices=(3,8))
                size = scene.size
                raw_slice = np.reshape(raw_slice, (size[1],size[0]))
                slice_roi = raw_slice[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
                image_slice = image[2, :, :, 1]
                score = compare_images(image_slice.copy(), slice_roi.copy())
                self.assertEqual(score, 1)


if __name__ == '__main__':
    unittest.main()
