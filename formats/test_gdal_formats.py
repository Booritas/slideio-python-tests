"""Codec coverage for the GDAL driver: JPEG 2000, JPEG and JPEG XR.

These formats had no tests of their own.  Opening a file only proves the driver
did not crash, so each case is checked against an uncompressed sibling of the
same picture that already ships in the corpus: the decoded pixels must agree.
That catches a broken or missing codec, which a smoke test would not.
"""
import sys

import numpy as np
import pytest
import slideio

from common.test_tools import image_path, compute_similarity

# name -> compressed file, uncompressed sibling, size, similarity floor.
# The lossless codecs must reproduce the sibling exactly; the JPEG pairs are
# lossy, so they are held to a high floor rather than to equality.
PAIRS = {
    "jpeg2000": (("jp2K", "relax.jp2"), ("jp2K", "relax.bmp"), (400, 300), 1.0),
    "jpegxr_wdp": (("jxr", "seagull.wdp"), ("jxr", "seagull.bmp"), (1000, 667), 1.0),
    "jpeg_lena": (("jpeg", "lena_256.jpg"), ("jpeg", "lena_256.png"), (256, 256), 0.999),
    "jpeg_photo": (("jpeg", "p2YCpvg.jpeg"), ("jpeg", "p2YCpvg.png"), (1452, 800), 0.999),
}

# Files with no uncompressed sibling: geometry and a readable raster only.
SINGLES = {
    "jpegxr_sample": (("jxr", "sample.jxr"), (128, 128)),
    "jpegxr_tissue": (("jxr", "tissue.jxr"), (550, 345)),
}

# The FreeImage build shipped in the macOS wheels has no JPEG XR plugin: it
# loads these files as FIT_UNKNOWN and slideio raises "Unsupported FreeImage
# type".
UNSUPPORTED_ON_MACOS_LINUX = {"jpegxr_wdp", "jpegxr_sample", "jpegxr_tissue"}


def platform_params(keys):
    """Wrap keys as pytest params, skipping those macOS cannot decode."""
    return [
        pytest.param(key, marks=pytest.mark.skipif(
            (sys.platform == "darwin" or sys.platform == "linux") and key in UNSUPPORTED_ON_MACOS_LINUX,
            reason="FreeImage on macOS lacks JPEG XR support"))
        for key in keys
    ]


@pytest.fixture
def gdal_scene(opened_slide):
    def _scene(fmt, subpath):
        return opened_slide(image_path(fmt, subpath), "GDAL").get_scene(0)
    return _scene


class TestCompressedAgainstUncompressed:

    @pytest.mark.parametrize("key", platform_params(sorted(PAIRS)))
    def test_geometry_matches_the_sibling(self, key, gdal_scene):
        compressed, uncompressed, size, _ = PAIRS[key]
        left, right = gdal_scene(*compressed), gdal_scene(*uncompressed)
        assert left.size == size
        assert right.size == size
        assert left.num_channels == right.num_channels == 3
        assert left.get_channel_data_type(0) == np.uint8

    @pytest.mark.parametrize("key", platform_params(sorted(PAIRS)))
    def test_decoded_pixels_match_the_sibling(self, key, gdal_scene):
        compressed, uncompressed, _, floor = PAIRS[key]
        left = gdal_scene(*compressed).read_block()
        right = gdal_scene(*uncompressed).read_block()
        assert left.shape == right.shape
        assert compute_similarity(left, right) >= floor

    @pytest.mark.parametrize(
        "key", platform_params(k for k, v in PAIRS.items() if v[3] == 1.0))
    def test_lossless_codecs_reproduce_the_sibling_exactly(self, key, gdal_scene):
        compressed, uncompressed, _, _ = PAIRS[key]
        left = gdal_scene(*compressed).read_block()
        right = gdal_scene(*uncompressed).read_block()
        assert np.array_equal(left, right)


class TestSingleFiles:

    @pytest.mark.parametrize("key", platform_params(sorted(SINGLES)))
    def test_geometry(self, key, gdal_scene):
        location, size = SINGLES[key]
        scene = gdal_scene(*location)
        assert scene.size == size
        assert scene.num_channels == 3

    @pytest.mark.parametrize("key", platform_params(sorted(SINGLES)))
    def test_full_read(self, key, gdal_scene):
        location, size = SINGLES[key]
        raster = gdal_scene(*location).read_block()
        assert raster.shape == (size[1], size[0], 3)
        assert raster.dtype == np.uint8


class TestCompressionReporting:
    """The compression the scene reports must name the codec of the file."""

    @pytest.mark.parametrize("fmt,subpath,compression", [
        ("jp2K", "relax.jp2", slideio.Compression.Jpeg2000),
        ("jpeg", "lena_256.jpg", slideio.Compression.Jpeg),
        ("jp2K", "relax.bmp", slideio.Compression.Uncompressed),
    ])
    def test_compression(self, fmt, subpath, compression, gdal_scene):
        assert gdal_scene(fmt, subpath).compression == compression


class TestPartialReads:

    def test_block_matches_the_same_region_of_the_full_raster(self, gdal_scene):
        """A sub-rect read must equal that slice of the whole image."""
        scene = gdal_scene("jp2K", "relax.jp2")
        full = scene.read_block()
        block = scene.read_block(rect=(100, 50, 128, 96))
        assert np.array_equal(block, full[50:146, 100:228])

    def test_rescaled_block(self, gdal_scene):
        raster = gdal_scene("jpeg", "lena_256.jpg").read_block(
            rect=(0, 0, 256, 256), size=(64, 64))
        assert raster.shape == (64, 64, 3)
