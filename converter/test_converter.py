import unittest
import slideio
import os
import sys
from PIL import Image
import numpy as np
import json
import tempfile
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compute_similarity

def create_output_file_path(extension):
    temp_dir = tempfile.gettempdir()
    filename = f"temp_{uuid.uuid4()}{extension}"
    return os.path.join(temp_dir, filename)

class TestConvertOmetiff(unittest.TestCase):
    """Tests for slideio GDAL driver functionality."""
    def test_convert_jpeg(self):
        image_path =Tools().getImageFilePath("gdal","Airbus_Pleiades_50cm_8bit_RGB_Yogyakarta.jpg",ImageDir.PUBLIC)
        output_path = create_output_file_path(".ome.tiff")
        with slideio.open_slide(image_path, "GDAL") as slide:
            self.assertTrue(slide is not None)
            with slide.get_scene(0) as scene:
                params = slideio.OMETIFFJpegParameters()
                # Conversion
                slideio.convert_scene(scene, params, output_path)
                with slideio.open_slide(output_path, "OMETIFF") as converted_slide:
                    self.assertTrue(converted_slide is not None)
                    self.assertEqual(converted_slide.num_scenes, 1)
                    with converted_slide.get_scene(0) as converted_scene:
                        self.assertEqual(converted_scene.size[0], scene.size[0])
                        self.assertEqual(converted_scene.size[1], scene.size[1])
                        block = scene.read_block((0,0,1000,1500))
                        converted_block = converted_scene.read_block((0,0,1000,1500))
                        sim = compute_similarity(block, converted_block)
                        self.assertGreater(sim, 0.99, "Images are not similar enough")
                                                
class TestConvertSVS(unittest.TestCase):
    """Tests for slideio GDAL driver functionality."""
    def test_convert_jpeg2SVS(self):
        image_path =Tools().getImageFilePath("gdal","Airbus_Pleiades_50cm_8bit_RGB_Yogyakarta.jpg",ImageDir.PUBLIC)
        output_path = create_output_file_path(".svs")
        with slideio.open_slide(image_path, "GDAL") as slide:
            self.assertTrue(slide is not None)
            with slide.get_scene(0) as scene:
                params = slideio.SVSJpegParameters()
                # Conversion
                slideio.convert_scene(scene, params, output_path)
                with slideio.open_slide(output_path, "SVS") as converted_slide:
                    self.assertTrue(converted_slide is not None)
                    self.assertEqual(converted_slide.num_scenes, 1)
                    with converted_slide.get_scene(0) as converted_scene:
                        self.assertEqual(converted_scene.size[0], scene.size[0])
                        self.assertEqual(converted_scene.size[1], scene.size[1])
                        block = scene.read_block((0,0,1000,1500))
                        converted_block = converted_scene.read_block((0,0,1000,1500))
                        sim = compute_similarity(block, converted_block)
                        self.assertGreater(sim, 0.99, "Images are not similar enough")
                                                