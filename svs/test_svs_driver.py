"""slideio CZI driver testing."""

import unittest
import pytest
import cv2 as cv
import numpy as np
import slideio

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.test_tools import Tools, ImageDir, compare_images, compute_similarity


class TestSVS(unittest.TestCase):
    """Tests for slideio CZI driver functionality."""

    def test_not_existing_file(self):
        """
        Opening of not existing image.

        Checks if slideio throws RuntimeError
        exception during opening of not existing file.
        """
        image_path = "missing_file.png"
        with pytest.raises(RuntimeError):
            slideio.open_slide(image_path, "SVS")

    def test_file_j2k_metadata(self):
        """
        Checks image metadata.

        Opens 3 channel Jpeg 2000 commpressed file
        and checks metadata.
        """
        image_path =Tools().getImageFilePath("svs","JP2K-33003-1.svs",ImageDir.PUBLIC)
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        self.assertEqual(image_path, slide.file_path)

        raw_metadata = slide.raw_metadata
        self.assertTrue(raw_metadata.startswith("Aperio Image Library"))

        # auxiliary images
        self.assertEqual(slide.num_aux_images, 3)
        aux_image_names = slide.get_aux_image_names().sort()
        names = ["Thumbnail", "Label", "Macro"].sort()
        self.assertEqual(names, aux_image_names)
        thumbnail = slide.get_aux_image_raster("Thumbnail")
        self.assertEqual(thumbnail.shape, (768, 674, 3))
        label = slide.get_aux_image_raster("Label")
        self.assertEqual(label.shape, (422, 415, 3))
        macro = slide.get_aux_image_raster("Macro")
        self.assertEqual(macro.shape, (421, 1280, 3))

        # test scene metadates
        compression_types = [slideio.Compression.Jpeg2000]
        scene_sizes = [(15374, 17497)]
        scene_magnifications = [40.]
        scene_names = ["Image"]

        for scene_index in range(num_scenes):
            scene = slide.get_scene(scene_index)
            self.assertTrue(scene is not None)
            scene_rect = scene.rect
            scene_size = (scene_rect[2], scene_rect[3])
            self.assertEqual(scene.name, scene_names[scene_index])
            self.assertEqual(scene.compression, compression_types[scene_index])
            self.assertEqual(scene.num_channels, 3)
            self.assertEqual(scene_size, scene_sizes[scene_index])
            self.assertEqual(image_path, scene.file_path)
            self.assertEqual(
                scene_magnifications[scene_index],
                scene.magnification
            )
            for channel_index in range(scene.num_channels):
                channel_type = scene.get_channel_data_type(channel_index)
                self.assertEqual(channel_type, np.uint8)

        # test scene resolutuion
        scene_resolutions = [0.2498e-6]
        for scene_index in range(num_scenes):
            scene = slide.get_scene(scene_index)
            self.assertTrue(scene is not None)
            res = scene.resolution
            self.assertEqual(
                scene_resolutions[scene_index],
                pytest.approx(res[0])
                )
            self.assertEqual(
                scene_resolutions[scene_index],
                pytest.approx(res[1])
                )

    def test_file_rgb_metadata(self):
        """
        Checks image metadata.

        Opens 3 channel brightfield Jpeg commpressed file
        and checks metadata.
        """
        image_path =Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        self.assertEqual(image_path, slide.file_path)

        raw_metadata = slide.raw_metadata
        self.assertTrue(raw_metadata.startswith("Aperio Image Library"))

        # auxiliary images
        self.assertEqual(slide.num_aux_images, 3)
        aux_image_names = slide.get_aux_image_names().sort()
        names = ["Thumbnail", "Label", "Macro"].sort()
        self.assertEqual(names, aux_image_names)
        thumbnail = slide.get_aux_image_raster("Thumbnail")
        self.assertEqual(thumbnail.shape, (768, 574, 3))
        label = slide.get_aux_image_raster("Label")
        self.assertEqual(label.shape, (463, 387, 3))
        macro = slide.get_aux_image_raster("Macro")
        self.assertEqual(macro.shape, (431, 1280, 3))


        # test scene metadates
        scene_names = ["Image"]
        compression_types = [
            slideio.Compression.Jpeg,
            ]
        scene_sizes = [
            (2220, 2967),
            ]
        scene_magnifications = [20.]

        for scene_index in range(num_scenes):
            scene = slide.get_scene(scene_index)
            self.assertTrue(scene is not None)
            scene_rect = scene.rect
            scene_size = (scene_rect[2], scene_rect[3])
            self.assertEqual(scene.name, scene_names[scene_index])
            self.assertEqual(scene.compression, compression_types[scene_index])
            self.assertEqual(scene.num_channels, 3)
            self.assertEqual(scene_size, scene_sizes[scene_index])
            self.assertEqual(image_path, scene.file_path)
            self.assertEqual(
                scene_magnifications[scene_index],
                scene.magnification
            )
            for channel_index in range(scene.num_channels):
                channel_type = scene.get_channel_data_type(channel_index)
                self.assertEqual(channel_type, np.uint8)

        # test scene resolutuion
        scene_resolutions = [0.4990e-6]
        for scene_index in range(num_scenes):
            scene = slide.get_scene(scene_index)
            self.assertTrue(scene is not None)
            res = scene.resolution
            self.assertEqual(
                scene_resolutions[scene_index],
                pytest.approx(res[0])
                )
            self.assertEqual(
                scene_resolutions[scene_index],
                pytest.approx(res[1])
                )

    def test_file_rgb_metadata_pictures(self):
        """
        Checks image metadata pictures.

        Opens 3 channel brightfield Jpeg commpressed file
        and checks metadata pictures agains extracted by
        a 3rd party tools pictures.
        """
        image_path =Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        metadata_pic_paths = {
            "Thumbnail" : Tools().getTestImagePath(
                "svs",
                "CMU-1-Small-Region-page-1.tif"
            ),
            "Label" : Tools().getTestImagePath(
                "svs",
                "CMU-1-Small-Region-page-2.tif"
            ),
            "Macro": Tools().getTestImagePath(
                "svs",
                "CMU-1-Small-Region-page-3.tif"
            ),
        }
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_aux_images = slide.num_aux_images
        self.assertEqual(num_aux_images, 3)
        image_names = slide.get_aux_image_names()
        for image_name in image_names:
            image = slide.get_aux_image_raster(image_name, channel_indices=[2, 1, 0])
            reference_image = cv.imread(
                metadata_pic_paths[image_name],
                cv.IMREAD_UNCHANGED
                )
            self.assertEqual(image.shape, reference_image.shape)
            score = compare_images(image, reference_image)
            self.assertEqual(score, 1)

    def test_file_rgb_image(self):
        """
        Checks image raster pictures.

        Opens 3 channel brightfield Jpeg commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","CMU-1-Small-Region-page-0.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        scene_image = scene.read_block()
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        self.assertEqual(scene_image.shape, reference_image.shape)
        self.assertTrue(np.array_equal(scene_image, reference_image))

    def test_file_rgb_image_region(self):
        """
        Checks reading of an image region.

        Opens 3 channel brightfield Jpeg commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","CMU-1-Small-Region-page-0.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 500
        y_beg = 500
        width = 600
        height = 300
        rect = (x_beg, y_beg, width, height)
        scene_image = scene.read_block(rect)
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        x_end = x_beg + width
        y_end = y_beg + height
        reference_region = reference_image[y_beg:y_end, x_beg:x_end]
        self.assertEqual(scene_image.shape, reference_region.shape)
        self.assertTrue(np.array_equal(scene_image, reference_region))

    def test_file_rgb_image_region_resizing(self):
        """
        Checks reading of an image region with resizing.

        Opens 3 channel brightfield Jpeg commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","CMU-1-Small-Region-page-0.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 500
        y_beg = 500
        width = 600
        height = 300
        params = [
            ((400, 200), (0.0011, 0.98)),
            ((200, 100), (0.012, 0.83))
        ]
        rect = (x_beg, y_beg, width, height)
        x_end = x_beg + width
        y_end = y_beg + height
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        reference_image = reference_image[y_beg:y_end, x_beg:x_end]
        for param in params:
            size = param[0]
            cf_threshold = param[1][1]
            sq_threshold = param[1][0]
            scene_image = scene.read_block(rect, size=size)
            reference_region = cv.resize(reference_image, size)
            self.assertEqual(scene_image.shape, reference_region.shape)
            score_sq = cv.matchTemplate(
                scene_image,
                reference_region,
                cv.TM_SQDIFF_NORMED
                )[0][0]
            score_cf = cv.matchTemplate(
                scene_image,
                reference_region,
                cv.TM_CCOEFF_NORMED
                )[0][0]
            self.assertLess(score_sq, sq_threshold)
            self.assertLess(cf_threshold, score_cf)

    def test_file_rgb_image_channel_swap(self):
        """
        Checks image raster pictures.

        Reads 3 channel brightfield Jpeg commpressed file
        with channel swaping and checks raster against
        extracted by a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","CMU-1-Small-Region-page-0.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        scene_image = scene.read_block(
            channel_indices=[2, 1, 0]
            )
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        self.assertEqual(scene_image.shape, reference_image.shape)
        self.assertTrue(np.array_equal(scene_image, reference_image))

    def test_file_jp2k_image_region(self):
        """
        Checks reading of an image region.

        Opens 3 channel brightfield Jpeg2K commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","JP2K-33003-1.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","JP2K-33003-1-region_x4000_y4000_w3000_h1500.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 4000
        y_beg = 4000
        width = 3000
        height = 1500
        rect = (x_beg, y_beg, width, height)
        scene_image = scene.read_block(rect)
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_region = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        self.assertEqual(scene_image.shape, reference_region.shape)

        score_sq = cv.matchTemplate(
            scene_image,
            reference_region,
            cv.TM_SQDIFF_NORMED
            )[0][0]
        score_cf = cv.matchTemplate(
            scene_image,
            reference_region,
            cv.TM_CCOEFF_NORMED
            )[0][0]

        self.assertLess(score_sq, 0.00125)
        self.assertLess(0.99, score_cf)

    def test_file_jp2k_image_region_resize(self):
        """
        Checks reading of an image region with resizing.

        Opens 3 channel brightfield Jpeg2K commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","JP2K-33003-1.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","JP2K-33003-1-region_x4000_y4000_w3000_h1500.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 4000
        y_beg = 4000
        width = 3000
        height = 1500
        rect = (x_beg, y_beg, width, height)
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        scaling_params = [
            (1.0, 0.99, 0.0013),
            (1.5, 0.93, 0.007),
            (2.0, 0.99, 0.0009),
            (3.0, 0.90, 0.01),
            (5.0, 0.84, 0.015)
            ]
        for param in scaling_params:
            scale = param[0]
            cf_threshold = param[1]
            sq_threshold = param[2]
            new_size = (
                int(round(reference_image.shape[1]/scale)),
                int(round(reference_image.shape[0]/scale))
                )
            reference_region = cv.resize(reference_image, new_size)
            image_region = scene.read_block(rect, size=new_size)
            self.assertEqual(image_region.shape, reference_region.shape)

            score_sq = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_SQDIFF_NORMED
                )[0][0]
            score_cf = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_CCOEFF_NORMED
                )[0][0]

            self.assertLess(score_sq, sq_threshold)
            self.assertLess(cf_threshold, score_cf)

    def test_file_jp2k_image_region_resize_1channel(self):
        """
        Checks reading of an image region with resizing.

        Read 1 channel region form brightfield Jpeg2K
        commpressed image and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","JP2K-33003-1.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","JP2K-33003-1-region_x4000_y4000_w3000_h1500.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 4000
        y_beg = 4000
        width = 3000
        height = 1500
        rect = (x_beg, y_beg, width, height)
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)
        reference_image = cv.extractChannel(reference_image, 1)

        scaling_params = [
            (2.0, 0.99, 0.0009)
            ]

        for param in scaling_params:
            scale = param[0]
            cf_threshold = param[1]
            sq_threshold = param[2]
            new_size = (
                int(round(reference_image.shape[1]/scale)),
                int(round(reference_image.shape[0]/scale))
                )
            reference_region = cv.resize(reference_image, new_size)
            image_region = scene.read_block(
                rect,
                size=new_size,
                channel_indices=[1]
                )
            self.assertEqual(image_region.shape, reference_region.shape)

            score_sq = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_SQDIFF_NORMED
                )[0][0]
            score_cf = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_CCOEFF_NORMED
                )[0][0]

            self.assertLess(score_sq, sq_threshold)
            self.assertLess(cf_threshold, score_cf)

    def test_file_jp2k_image_region_resize_swap_channels(self):
        """
        Checks reading of an image region with resizing.

        Opens 3 channel brightfield Jpeg2K commpressed file
        and checks raster agains extracted by
        a 3rd party tools pictures.
        """
        image_path = Tools().getImageFilePath("svs","JP2K-33003-1.svs",ImageDir.PUBLIC)
        reference_image_path = Tools().getTestImagePath("svs","JP2K-33003-1-region_x4000_y4000_w3000_h1500.tif")
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        num_scenes = slide.num_scenes
        self.assertEqual(num_scenes, 1)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        x_beg = 4000
        y_beg = 4000
        width = 3000
        height = 1500
        rect = (x_beg, y_beg, width, height)
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )

        scaling_params = [
            (2.0, 0.99, 0.0009)
            ]

        for param in scaling_params:
            scale = param[0]
            cf_threshold = param[1]
            sq_threshold = param[2]
            new_size = (
                int(round(reference_image.shape[1]/scale)),
                int(round(reference_image.shape[0]/scale))
                )
            reference_region = cv.resize(reference_image, new_size)
            image_region = scene.read_block(
                rect,
                size=new_size,
                channel_indices=[2, 1, 0]
                )
            self.assertEqual(image_region.shape, reference_region.shape)

            score_sq = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_SQDIFF_NORMED
                )[0][0]
            score_cf = cv.matchTemplate(
                image_region,
                reference_region,
                cv.TM_CCOEFF_NORMED
                )[0][0]

            self.assertLess(score_sq, sq_threshold)
            self.assertLess(cf_threshold, score_cf)

    def test_rgb_jpeg_regression(self):
        """
        Regression test for rgb jpeg compressed image.

        Read the block from a slide and compares it
        with a reference image. The reference image
        is obtained by reading of the same region
        by the slideo and saving it as a png file.
        """
        # Image to test
        image_path = Tools().getImageFilePath("svs","CMU-1-Small-Region.svs",ImageDir.PUBLIC)
        # Image to test
        reference_image_path = Tools().getTestImagePath("svs","CMU-1-Small-Region.regression_x700_y400_w500_y400.png")
        # Read reference image
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        x_beg = 700
        y_beg = 400
        width = 500
        height = 400
        rect = (x_beg, y_beg, width, height)
        new_size = (100, 80)

        # open the slide
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        block_raster = scene.read_block(
            rect,
            size=new_size
            )
        self.assertTrue(np.array_equal(block_raster, reference_image))

    def test_rgb_jp2k_regression(self):
        """
        Regression test for rgb jp2k compressed image.

        Read the block from a slide and compares it
        with a reference image. The reference image
        is obtained by reading of the same region
        by the slideo and saving it as a png file.
        """
        # Image to test
        image_path = Tools().getImageFilePath("svs","JP2K-33003-1.svs", ImageDir.PUBLIC)
        # Image to test
        reference_image_path = Tools().getTestImagePath("svs","JP2K-33003-1.regression_x4000_y4000_w500_y400.png")
        # Read reference image
        reference_image = cv.imread(
            reference_image_path,
            cv.IMREAD_UNCHANGED
            )
        x_beg = 4000
        y_beg = 4000
        width = 500
        height = 400
        rect = (x_beg, y_beg, width, height)
        new_size = (100, 80)

        # open the slide
        slide = slideio.open_slide(image_path, "SVS")
        self.assertTrue(slide is not None)
        scene = slide.get_scene(0)
        self.assertTrue(scene is not None)
        block_raster = scene.read_block(
            rect,
            size=new_size
            )
        
        sim_score = compute_similarity(block_raster, reference_image)
        self.assertGreater(sim_score, 0.999)


if __name__ == '__main__':
    unittest.main()
