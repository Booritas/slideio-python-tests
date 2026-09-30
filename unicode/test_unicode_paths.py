# -*- coding: utf-8 -*-
"""Opening images whose path contains non-ASCII characters.

The corpus carries a directory named with Cyrillic characters holding one file
per driver family.  Path handling is where a C++ binding is most likely to break
on Windows, since the path crosses from Python str into a narrow std::string and
back, so each driver is exercised rather than one representative.
"""
import numpy as np
import pytest

from common.test_tools import image_path

UNICODE_DIR = "\u0442\u0435\u0441\u0442"  # "тест"

# driver -> file in the Cyrillic directory, scene size, channel count
CASES = {
    "SVS": ("CMU-1-Small-Region.svs", (2220, 2967), 3),
    "SCN": ("Leica-Fluorescence-1.scn", (4737, 6338), 3),
    "GDAL": ("lena_256.jpg", (256, 256), 3),
    "CZI": ("pJP31mCherry.czi", (512, 512), 3),
    "NDPI": ("test3-TRITC 2 (560).ndpi", (3968, 4864), 3),
    "ZVI": ("TOMMAlexaFluor647.zvi", (1388, 1040), 1),
}

# A file whose own name is non-ASCII, not just its directory.
UNICODE_FILENAME = ("GDAL", "\u0442\u0435\u0441\u0442.tif", (387, 463))


def unicode_image(subpath):
    return image_path("unicode", f"{UNICODE_DIR}/{subpath}")


@pytest.fixture
def unicode_slide(opened_slide):
    def _open(driver, subpath):
        return opened_slide(unicode_image(subpath), driver)
    return _open


class TestUnicodeDirectory:

    @pytest.mark.parametrize("driver", sorted(CASES))
    def test_scene_geometry(self, driver, unicode_slide):
        subpath, size, channels = CASES[driver]
        scene = unicode_slide(driver, subpath).get_scene(0)
        assert scene.size == size
        assert scene.num_channels == channels

    @pytest.mark.parametrize("driver", sorted(CASES))
    def test_block_read(self, driver, unicode_slide):
        """Pixels must come back, not just metadata: the path is reopened for
        raster access in several drivers."""
        subpath, _, channels = CASES[driver]
        scene = unicode_slide(driver, subpath).get_scene(0)
        raster = scene.read_block(rect=(0, 0, 64, 64))
        expected = (64, 64, channels) if channels > 1 else (64, 64)
        assert raster.shape == expected
        assert raster.size > 0

    @pytest.mark.parametrize("driver", sorted(CASES))
    def test_scene_reports_the_path_it_was_given(self, driver, unicode_slide):
        subpath, _, _ = CASES[driver]
        slide = unicode_slide(driver, subpath)
        assert slide.get_scene(0).file_path == unicode_image(subpath)

    @pytest.mark.parametrize("driver", sorted(CASES))
    def test_slide_reports_the_path_it_was_given(self, driver, unicode_slide):
        """ZVI is included: it returned an empty path until 2.10.0 was fixed."""
        subpath, _, _ = CASES[driver]
        slide = unicode_slide(driver, subpath)
        assert slide.file_path == unicode_image(subpath)


class TestUnicodeFilename:

    def test_non_ascii_filename(self, unicode_slide):
        driver, subpath, size = UNICODE_FILENAME
        scene = unicode_slide(driver, subpath).get_scene(0)
        assert scene.size == size
        assert scene.read_block(rect=(0, 0, 64, 64)).shape == (64, 64, 3)


class TestMissingUnicodePath:

    def test_missing_file_in_unicode_directory_raises(self):
        import slideio
        with pytest.raises(RuntimeError):
            slideio.open_slide(f"{UNICODE_DIR}/missing_file.svs", "SVS")
