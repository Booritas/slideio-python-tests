"""Per-channel significant bits, introduced in slideio 2.10.

Scene.get_channel_significant_bits() reports how many bits the acquisition
actually filled, which can be narrower than the channel's storage type: a 16 bit
raster carrying 12 bits of camera data reports 12.  Formats that do not state it
report 0, which is why the value is not simply derived from the data type.
"""
import pytest

from common.test_tools import image_path

# driver, format dir, subpath, significant bits per channel
CASES = {
    # 16 bit storage, narrower acquisition - the case the API exists for.
    "czi_12bit": ("CZI", "czi", "jxr-16bit-4chnls.czi", [12, 12, 12, 12]),
    "afi_10bit": ("AFI", "afi", "fs.afi", [10]),
    # 16 bit storage fully used.
    "czi_16bit": ("CZI", "czi", "1000xRED autofluorescence Z-stack.czi", [16]),
    "czi_16bit_6chnl": ("CZI", "czi",
                        "03_14_2019_DSGN0545_A_wb_1353_fov_1_633.czi", [16] * 6),
    # 8 bit storage, stated.
    "czi_8bit": ("CZI", "czi", "pJP31mCherry.czi", [8, 8, 8]),
    "phtiff_8bit": ("PHTIFF", "philips", "Philips-1.tiff", [8, 8, 8]),
    "ometiff_8bit": ("OMETIFF", "ometiff",
                     "LAMBDA-ModuloAlongZ-ModuloAlongT.ome.tiff", [8]),
    # Formats that state nothing report 0 rather than guessing from the dtype.
    "svs_unstated": ("SVS", "svs", "JP2K-33003-1.svs", [0, 0, 0]),
    "gdal_unstated": ("GDAL", "gdal", "colors.png", [0, 0, 0]),
    "ndpi_unstated": ("NDPI", "hamamatsu", "HE_Hamamatsu.ndpi", [0, 0, 0]),
    "scn_unstated": ("SCN", "scn", "Leica-Fluorescence-1.scn", [0, 0, 0]),
}

# Cases where the value must be strictly narrower than the storage type, so a
# regression that returned the dtype width would be caught.
NARROWER_THAN_STORAGE = {
    "czi_12bit": ("CZI", "czi", "jxr-16bit-4chnls.czi", 16, 12),
    "afi_10bit": ("AFI", "afi", "fs.afi", 16, 10),
}


@pytest.fixture
def scene_of(opened_slide):
    def _scene(driver, fmt, subpath):
        return opened_slide(image_path(fmt, subpath), driver).get_scene(0)
    return _scene


class TestSignificantBits:

    @pytest.mark.parametrize("key", sorted(CASES))
    def test_reported_bits_per_channel(self, key, scene_of):
        driver, fmt, subpath, expected = CASES[key]
        scene = scene_of(driver, fmt, subpath)
        assert scene.num_channels == len(expected)
        actual = [scene.get_channel_significant_bits(channel)
                  for channel in range(scene.num_channels)]
        assert actual == expected

    @pytest.mark.parametrize("key", sorted(NARROWER_THAN_STORAGE))
    def test_value_is_narrower_than_the_storage_type(self, key, scene_of):
        """The whole point of the API: not derivable from the data type."""
        driver, fmt, subpath, storage_bits, expected = NARROWER_THAN_STORAGE[key]
        scene = scene_of(driver, fmt, subpath)
        assert scene.get_channel_data_type(0).itemsize * 8 == storage_bits
        assert scene.get_channel_significant_bits(0) == expected
        assert scene.get_channel_significant_bits(0) < storage_bits

    @pytest.mark.parametrize("channel", [99, -1])
    def test_out_of_range_channel_returns_zero(self, channel, scene_of):
        driver, fmt, subpath, _ = CASES["czi_12bit"]
        assert scene_of(driver, fmt, subpath).get_channel_significant_bits(channel) == 0
