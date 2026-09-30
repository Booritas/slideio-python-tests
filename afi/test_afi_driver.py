"""slideio AFI driver testing.

An AFI file is an Aperio fluorescence index: a small XML wrapper naming several
single-channel SVS files that share one geometry.  slideio presents each of them
as a scene of the same slide, so the things worth pinning are that all the
referenced files are found, that they agree on geometry, and that they carry
genuinely different pixel data rather than the same channel three times.
"""
import numpy as np
import pytest
import slideio

from common.test_tools import image_path

IMAGE = ("afi", "fs.afi")
SCENE_COUNT = 3
SCENE_SIZE = (9520, 15121)
MAGNIFICATION = 20.0
RESOLUTION = 4.654e-07
ZOOM_LEVELS = 3


@pytest.fixture
def afi_slide(opened_slide):
    return opened_slide(image_path(*IMAGE), "AFI")


class TestAfiSlide:

    def test_not_existing_file(self):
        with pytest.raises(RuntimeError):
            slideio.open_slide("missing_file.afi", "AFI")

    def test_driver_is_registered(self):
        assert "AFI" in slideio.get_driver_ids()

    def test_one_scene_per_referenced_channel_file(self, afi_slide):
        assert afi_slide.num_scenes == SCENE_COUNT

    def test_file_path(self, afi_slide):
        assert afi_slide.file_path == image_path(*IMAGE)


class TestAfiScenes:

    @pytest.mark.parametrize("index", range(SCENE_COUNT))
    def test_scene_geometry(self, index, afi_slide):
        """Every referenced file must describe the same slide."""
        scene = afi_slide.get_scene(index)
        assert scene.size == SCENE_SIZE
        assert scene.rect == (0, 0) + SCENE_SIZE
        assert scene.magnification == MAGNIFICATION
        assert scene.num_zoom_levels == ZOOM_LEVELS
        assert scene.resolution[0] == pytest.approx(RESOLUTION, rel=1e-4)
        assert scene.resolution[1] == pytest.approx(RESOLUTION, rel=1e-4)

    @pytest.mark.parametrize("index", range(SCENE_COUNT))
    def test_scene_is_single_channel_16_bit(self, index, afi_slide):
        scene = afi_slide.get_scene(index)
        assert scene.num_channels == 1
        assert scene.get_channel_data_type(0) == np.uint16
        assert scene.compression == slideio.Compression.Jpeg2000

    @pytest.mark.parametrize("index", range(SCENE_COUNT))
    def test_block_read(self, index, afi_slide):
        raster = afi_slide.get_scene(index).read_block(
            rect=(1000, 1000, 256, 256), size=(64, 64))
        assert raster.shape == (64, 64)
        assert raster.dtype == np.uint16

    def test_scenes_carry_different_channels(self, afi_slide):
        """Three fluorescence channels, not the same image three times."""
        rect, size = (1000, 1000, 256, 256), (64, 64)
        rasters = [afi_slide.get_scene(index).read_block(rect=rect, size=size)
                   for index in range(SCENE_COUNT)]
        for index, left in enumerate(rasters):
            for right in rasters[index + 1:]:
                assert not np.array_equal(left, right)
