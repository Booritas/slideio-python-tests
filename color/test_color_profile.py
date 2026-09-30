"""ICC colour profile reporting, introduced in slideio 2.10.

Scene.get_color_profile() returns the raw ICC bytes and
Scene.get_color_profile_info() the parsed header.  These tests pin what a Python
caller sees for images that carry a profile and for images that do not, and
prove the bytes are a genuine profile rather than merely non-empty by parsing
them with an independent ICC implementation.
"""
import io

import pytest
import slideio

from common.test_tools import image_path

ImageCms = pytest.importorskip("PIL.ImageCms")


# Images that carry an embedded profile, with the header values the 2.10 parser
# reports for them.
PROFILED = {
    "aperio": dict(
        driver="SVS", fmt="svs", subpath="JP2K-33003-1.svs",
        size=141992, description="ScanScope v1", manufacturer="", model="",
        version="2.4",
        data_space=slideio.IccColorSpace.RGB,
        connection_space=slideio.IccColorSpace.LAB,
        intent=slideio.RenderingIntent.PERCEPTUAL,
    ),
    "srgb_iec": dict(
        driver="GDAL", fmt="gdal",
        subpath="Airbus_Pleiades_50cm_8bit_RGB_Yogyakarta.jpg",
        size=3144, description="sRGB IEC61966-2.1",
        manufacturer="IEC http://www.iec.ch",
        model="IEC 61966-2.1 Default RGB colour space - sRGB",
        version="2.1",
        data_space=slideio.IccColorSpace.RGB,
        connection_space=slideio.IccColorSpace.XYZ,
        intent=slideio.RenderingIntent.RELATIVE_COLORIMETRIC,
    ),
    "gimp_srgb": dict(
        driver="GDAL", fmt="gdal", subpath="colors.png",
        size=672, description="GIMP built-in sRGB", manufacturer="GIMP",
        model="sRGB", version="4.3",
        data_space=slideio.IccColorSpace.RGB,
        connection_space=slideio.IccColorSpace.XYZ,
        intent=slideio.RenderingIntent.PERCEPTUAL,
    ),
}

# Images of the same formats that carry no profile at all.
UNPROFILED = {
    "svs_no_icc": ("SVS", "svs", "CMU-1-Small-Region.svs"),
    "jpeg_no_icc": ("GDAL", "jpeg", "lena_256.jpg"),
    "jp2k_no_icc": ("GDAL", "jp2K", "relax.jp2"),
}


@pytest.fixture
def profile_of(opened_slide):
    """Factory returning (raw_bytes, info) for a corpus image."""
    def _profile(driver, fmt, subpath):
        slide = opened_slide(image_path(fmt, subpath), driver)
        scene = slide.get_scene(0)
        return scene.get_color_profile(), scene.get_color_profile_info()
    return _profile


class TestEmbeddedProfiles:
    """Images whose scene carries an embedded ICC profile."""

    @pytest.mark.parametrize("key", sorted(PROFILED))
    def test_profile_is_reported_as_embedded(self, key, profile_of):
        case = PROFILED[key]
        _, info = profile_of(case["driver"], case["fmt"], case["subpath"])
        assert info.present is True
        assert info.source == slideio.ColorProfileSource.EMBEDDED

    @pytest.mark.parametrize("key", sorted(PROFILED))
    def test_header_fields(self, key, profile_of):
        case = PROFILED[key]
        _, info = profile_of(case["driver"], case["fmt"], case["subpath"])
        assert info.description == case["description"]
        assert info.manufacturer == case["manufacturer"]
        assert info.model == case["model"]
        assert info.version == case["version"]
        assert info.data_space == case["data_space"]
        assert info.connection_space == case["connection_space"]
        assert info.intent == case["intent"]

    @pytest.mark.parametrize("key", sorted(PROFILED))
    def test_raw_bytes_length_matches_reported_size(self, key, profile_of):
        case = PROFILED[key]
        raw, info = profile_of(case["driver"], case["fmt"], case["subpath"])
        assert isinstance(raw, bytes)
        assert info.size == case["size"]
        assert len(raw) == info.size

    @pytest.mark.parametrize("key", sorted(PROFILED))
    def test_raw_bytes_parse_as_a_real_icc_profile(self, key, profile_of):
        """An independent ICC implementation must accept the bytes.

        Checking only that the buffer is non-empty would pass on any garbage the
        binding happened to hand back; round-tripping through ImageCms proves it
        is a profile, and that its description survives the trip.
        """
        case = PROFILED[key]
        raw, info = profile_of(case["driver"], case["fmt"], case["subpath"])
        parsed = ImageCms.getOpenProfile(io.BytesIO(raw))
        assert ImageCms.getProfileDescription(parsed).strip() == info.description

    @pytest.mark.parametrize("key", sorted(PROFILED))
    def test_white_point_is_a_three_component_vector(self, key, profile_of):
        case = PROFILED[key]
        _, info = profile_of(case["driver"], case["fmt"], case["subpath"])
        white_point = list(info.white_point)
        assert len(white_point) == 3
        assert all(0.0 < component < 2.0 for component in white_point)


class TestMissingProfiles:
    """Images with no embedded profile report absence rather than raising."""

    @pytest.mark.parametrize("key", sorted(UNPROFILED))
    def test_absent_profile_is_reported_as_none(self, key, profile_of):
        raw, info = profile_of(*UNPROFILED[key])
        assert info.present is False
        assert info.source == slideio.ColorProfileSource.NONE
        assert info.size == 0
        assert raw is None

    @pytest.mark.parametrize("key", sorted(UNPROFILED))
    def test_absent_profile_leaves_header_fields_empty(self, key, profile_of):
        _, info = profile_of(*UNPROFILED[key])
        assert info.description == ""
        assert info.manufacturer == ""
        assert info.model == ""
