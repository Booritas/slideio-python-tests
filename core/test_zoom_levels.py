"""Reading from an explicitly named zoom level.

read_block picks a level itself from the requested scaling.  read_block_from_level
reads the level you name, in that level's own pixel coordinates, with no implicit
selection.  These tests pin the relationship between the two and the level
geometry that get_zoom_level_info reports.
"""
import numpy as np
import pytest

from common.test_tools import image_path

# A pyramidal Aperio slide: 3 levels, each a quarter of the previous in area.
PYRAMID = ("SVS", "svs", "JP2K-33003-1.svs")
LEVEL_SIZES = {0: (15374, 17497), 1: (3843, 4374), 2: (1921, 2187)}
LEVEL_MAGNIFICATIONS = {0: 40.0, 1: 9.9987, 2: 4.99805}


@pytest.fixture
def pyramid_scene(opened_slide):
    driver, fmt, subpath = PYRAMID
    return opened_slide(image_path(fmt, subpath), driver).get_scene(0)


class TestZoomLevelInfo:

    def test_level_count(self, pyramid_scene):
        assert pyramid_scene.num_zoom_levels == len(LEVEL_SIZES)

    @pytest.mark.parametrize("level", sorted(LEVEL_SIZES))
    def test_level_geometry(self, level, pyramid_scene):
        info = pyramid_scene.get_zoom_level_info(level)
        width, height = LEVEL_SIZES[level]
        assert info.level == level
        assert (info.size.width, info.size.height) == (width, height)
        assert info.tile_size.width > 0 and info.tile_size.height > 0

    @pytest.mark.parametrize("level", sorted(LEVEL_SIZES))
    def test_scale_and_magnification_agree_with_size(self, level, pyramid_scene):
        info = pyramid_scene.get_zoom_level_info(level)
        assert info.scale == pytest.approx(
            LEVEL_SIZES[level][0] / LEVEL_SIZES[0][0], rel=1e-3)
        assert info.magnification == pytest.approx(
            LEVEL_MAGNIFICATIONS[level], rel=1e-4)


class TestReadBlockFromLevel:

    def test_unscaled_level_zero_matches_read_block(self, pyramid_scene):
        """With no rescaling, naming level 0 is the same read read_block does."""
        rect = (1000, 1000, 256, 256)
        assert np.array_equal(pyramid_scene.read_block_from_level(0, rect=rect),
                              pyramid_scene.read_block(rect=rect))

    def test_rect_is_in_the_level_coordinate_system(self, pyramid_scene):
        """A zero width and height extends to the edge of the named level."""
        for level, (width, height) in LEVEL_SIZES.items():
            if level == 0:
                continue  # full level 0 would be a 15374x17497 read
            raster = pyramid_scene.read_block_from_level(level, rect=(0, 0, 0, 0))
            assert raster.shape[:2] == (height, width)

    def test_size_rescales_from_the_named_level(self, pyramid_scene):
        raster = pyramid_scene.read_block_from_level(
            1, rect=(1000, 1000, 512, 512), size=(128, 128))
        assert raster.shape == (128, 128, 3)

    def test_levels_return_different_pixels(self, pyramid_scene):
        """The same rect at two levels covers different ground, so it must differ."""
        rect, size = (1000, 1000, 512, 512), (128, 128)
        level_0 = pyramid_scene.read_block_from_level(0, rect=rect, size=size)
        level_1 = pyramid_scene.read_block_from_level(1, rect=rect, size=size)
        assert not np.array_equal(level_0, level_1)

    def test_channel_selection(self, pyramid_scene):
        raster = pyramid_scene.read_block_from_level(
            1, rect=(1000, 1000, 256, 256), channel_indices=[0])
        assert raster.shape == (256, 256)

    @pytest.mark.parametrize("level", [99, -1, 3])
    def test_invalid_level_raises(self, level, pyramid_scene):
        with pytest.raises(RuntimeError):
            pyramid_scene.read_block_from_level(level, rect=(0, 0, 100, 100))
