import unittest
import slideio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_tools import TestTools
from test_tools import TestImageDir

class TestVsi(unittest.TestCase):

    def test_vsi_open(self):
        filePath = TestTools().getImageTestFilePath("vsi", "OS-1/OS-1.vsi", TestImageDir.FULL)
        slide = slideio.open_slide(filePath, "VSI")
        self.assertIsNotNone(slide)
        num_scenes = slide.num_scenes
        self.assertEqual(1, num_scenes)
        scene = slide.get_scene(0)
        scene_rect = (0,0,66982,76963)
        self.assertEqual(scene_rect, scene.rect)
        self.assertIsNotNone(scene)
        num_channels = scene.num_channels
        self.assertEqual(3, num_channels)
        self.assertEqual(scene.magnification, 20.)
        
if __name__ == '__main__':
    unittest.main()