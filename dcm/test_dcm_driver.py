"""slideio CZI driver testing."""

import unittest
import pytest
import numpy as np
import slideio
import sys
import os
import json
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity


class TestDCM(unittest.TestCase):
    """Tests for slideio DCM driver functionality."""

    def test_open_file(self):
        file_path =Tools().getImageFilePath("dcm","benigns_01/patient0186/0186.LEFT_CC.dcm",ImageDir.PUBLIC)
        with slideio.open_slide(file_path, "DCM") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,3984, 5528))
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.name,"case0377")
                self.assertEqual(scene.compression, slideio.Compression.Jpeg)
                self.assertEqual(scene.get_channel_data_type(0), np.uint16)

    def test_open_3d_image(self):
        file_path =Tools().getImageFilePath("dcm","series/series_1",ImageDir.PRIVATE)
        with slideio.open_slide(file_path, "DCM") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0,0,512, 512))
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.num_z_slices, 15)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.name,"COU IV")
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                self.assertEqual(scene.get_channel_data_type(0), np.uint16)

    def test_open_directory_recursively(self):
        file_path =Tools().getImageFilePath("dcm","series",ImageDir.PRIVATE)
        with slideio.open_slide(file_path, "DCM") as slide:
            self.assertEqual(slide.num_scenes, 2)
            index = 0
            if slide.get_scene(index).name == 'COU IV':
                index = 1
            with slide.get_scene(index) as scene:
                self.assertEqual(scene.rect, (0,0,512, 512))
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.num_z_slices, 9)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.name,"1.2.276.0.7230010.3.100.1.1")
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)

    def test_metadata(self):
        file_path =Tools().getImageFilePath("dcm","barre.dev/OT-MONO2-8-hip.dcm",ImageDir.PUBLIC)
        with slideio.open_slide(file_path, "DCM") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                metadata = scene.get_raw_metadata()
                try:
                    json_data = json.loads(metadata)
                    assert isinstance(json_data, dict)  # Ensure the parsed JSON is a dictionary
                except (ValueError, TypeError) as e:
                    raise AssertionError("Metadata is not a valid JSON string") from e
                self.assertEqual(scene.rect, (0,0,512, 512))
                self.assertEqual(scene.num_channels, 1)
                self.assertEqual(scene.num_z_slices, 1)
                self.assertEqual(scene.num_t_frames, 1)
                self.assertEqual(scene.name,"1.3.46.670589.17.1.7.2.1.23")
                self.assertEqual(scene.compression, slideio.Compression.Uncompressed)
                self.assertEqual(scene.get_channel_data_type(0), np.uint8)

    def test_read_with_resize(self):
        image_path =Tools().getImageFilePath("dcm","barre.dev/OT-MONO2-8-hip.dcm",ImageDir.PUBLIC)
        test_image_path = Tools().getImageFilePath("dcm","barre.dev/OT-MONO2-8-hip.frames/frame0.png",ImageDir.PUBLIC)
        with slideio.open_slide(image_path, "DCM") as slide:
            self.assertEqual(slide.num_scenes, 1)
            with slide.get_scene(0) as scene:
                rect = (100, 100, 400, 400)
                size = (200, 200)
                block = scene.read_block(rect=rect, size=size)
                test_image = Image.open(test_image_path).crop((100,100,500,500)).resize(size)
                similarity = compute_similarity(np.array(test_image), block)
                self.assertGreater(similarity, 0.99)
    

if __name__ == '__main__':
    unittest.main()
