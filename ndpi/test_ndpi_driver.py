"""slideio ZVI driver testing."""

import unittest
import pytest
import cv2 as cv
import numpy as np
import slideio
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compare_images


class TestNDPI(unittest.TestCase):
    """Tests for slideio NDPI driver functionality."""

    def test_openFile(self):
        """
        Open NDPI file

        """
        image_path =Tools().getImageFilePath("hamamatsu", "2017-02-27 15.29.08.ndpi",ImageDir.FULL)
            
        with slideio.open_slide(image_path, "NDPI") as slide:
            self.assertTrue(slide is not None)
            self.assertEqual(slide.num_scenes, 1)
            self.assertEqual(slide.num_aux_images, 2)
            self.assertEqual(slide.get_aux_image_names(), ["macro", "map"])
            with slide.get_scene(0) as scene:
                self.assertEqual(scene.rect, (0, 0, 11520, 9984))
                self.assertEqual(scene.num_channels, 3)


if __name__ == '__main__':
    unittest.main()
