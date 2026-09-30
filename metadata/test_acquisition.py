"""Acquisition time and per-plane timestamps, introduced in slideio 2.10.

Scene.acquisition_time is the scan start as seconds since the Unix epoch, or 0
when the format does not record one.  Scene.get_plane_timestamp() gives the
offset of a single plane from the scene origin, and is only meaningful when
has_plane_timestamps is True.
"""
import datetime

import pytest

from common.test_tools import image_path

# Formats that record a scan start, with the epoch the 2.10 readers extract and
# the UTC instant it decodes to.
WITH_ACQUISITION_TIME = {
    "svs_jp2k": ("SVS", "svs", "JP2K-33003-1.svs", 1247768106),
    "svs_cmu": ("SVS", "svs", "CMU-1-Small-Region.svs", 1262080755),
    "ndpi": ("NDPI", "hamamatsu", "HE_Hamamatsu.ndpi", 1398869490),
    "scn": ("SCN", "scn", "Leica-Fluorescence-1.scn", 1335967229),
    "afi": ("AFI", "afi", "fs.afi", 1263307110),
    "czi": ("CZI", "czi", "jxr-16bit-4chnls.czi", 1354888361),
    "ometiff": ("OMETIFF", "ometiff",
                "LAMBDA-ModuloAlongZ-ModuloAlongT.ome.tiff", 1316169948),
}

DECODED_UTC = {
    "ndpi": "2014-04-30T14:51:30",
    "scn": "2012-05-02T14:00:29",
    "afi": "2010-01-12T14:38:30",
    "czi": "2012-12-07T13:52:41",
    "ometiff": "2011-09-16T10:45:48",
}

# Formats that record none.  0 is the documented "not stated" value; these must
# not report a spurious epoch such as 1970-01-01 dressed up as a real time.
WITHOUT_ACQUISITION_TIME = {
    "png": ("GDAL", "gdal", "colors.png"),
    "jpeg": ("GDAL", "jpeg", "lena_256.jpg"),
    "czi_plain": ("CZI", "czi", "pJP31mCherry.czi"),
    "phtiff": ("PHTIFF", "philips", "Philips-1.tiff"),
}

# The one corpus image that carries per-plane timestamps, and its channel count.
TIMESTAMPED = ("CZI", "czi", "jxr-16bit-4chnls.czi", 4)


@pytest.fixture
def scene_of(opened_slide):
    def _scene(driver, fmt, subpath):
        return opened_slide(image_path(fmt, subpath), driver).get_scene(0)
    return _scene


class TestAcquisitionTime:

    @pytest.mark.parametrize("key", sorted(WITH_ACQUISITION_TIME))
    def test_reported_epoch(self, key, scene_of):
        driver, fmt, subpath, expected = WITH_ACQUISITION_TIME[key]
        assert scene_of(driver, fmt, subpath).acquisition_time == expected

    @pytest.mark.parametrize("key", sorted(DECODED_UTC))
    def test_epoch_decodes_to_the_expected_instant(self, key, scene_of):
        """Guards the unit as well as the value: seconds, not milliseconds."""
        driver, fmt, subpath, expected = WITH_ACQUISITION_TIME[key]
        moment = datetime.datetime.fromtimestamp(
            scene_of(driver, fmt, subpath).acquisition_time,
            datetime.timezone.utc)
        assert moment.replace(tzinfo=None).isoformat() == DECODED_UTC[key]

    @pytest.mark.parametrize("key", sorted(WITHOUT_ACQUISITION_TIME))
    def test_absent_time_is_zero(self, key, scene_of):
        assert scene_of(*WITHOUT_ACQUISITION_TIME[key]).acquisition_time == 0


class TestPlaneTimestamps:

    @pytest.mark.parametrize("key", sorted(WITHOUT_ACQUISITION_TIME))
    def test_formats_without_timestamps_say_so(self, key, scene_of):
        assert scene_of(*WITHOUT_ACQUISITION_TIME[key]).has_plane_timestamps is False

    @pytest.mark.parametrize("key", sorted(WITHOUT_ACQUISITION_TIME))
    def test_timestamp_of_untimestamped_scene_is_zero(self, key, scene_of):
        """Documented to return 0 rather than raise."""
        assert scene_of(*WITHOUT_ACQUISITION_TIME[key]).get_plane_timestamp(0, 0, 0) == 0.0

    def test_timestamped_scene_says_so(self, scene_of):
        driver, fmt, subpath, _ = TIMESTAMPED
        assert scene_of(driver, fmt, subpath).has_plane_timestamps is True

    def test_each_channel_has_its_own_offset(self, scene_of):
        """Channels of one frame are acquired in sequence, so offsets differ."""
        driver, fmt, subpath, channels = TIMESTAMPED
        scene = scene_of(driver, fmt, subpath)
        offsets = [scene.get_plane_timestamp(0, channel, 0) for channel in range(channels)]
        assert all(isinstance(offset, float) for offset in offsets)
        assert all(offset > 0.0 for offset in offsets)
        assert len(set(offsets)) == channels

    @pytest.mark.parametrize("t_frame,channel,z_slice", [
        (0, 99, 0),
        (99, 0, 0),
        (0, 0, 99),
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
    ])
    def test_out_of_range_indices_return_zero(self, t_frame, channel, z_slice, scene_of):
        driver, fmt, subpath, _ = TIMESTAMPED
        scene = scene_of(driver, fmt, subpath)
        assert scene.get_plane_timestamp(t_frame, channel, z_slice) == 0.0
