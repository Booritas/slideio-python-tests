"""The public surface of the slideio package.

The binding has three layers: the compiled slideiopybind module, the raw import
layer in slideio.core, and the public wrappers re-exported from slideio.  A type
that a public property hands back should be reachable from the public package,
otherwise callers have to import the private extension module to compare against
it.  These tests pin what 2.10 exports.
"""
import pytest
import slideio

# Everything a caller is expected to reach through `slideio.<name>`.
PUBLIC_NAMES = [
    # module functions
    "open_slide", "convert_scene", "transform_scene", "get_driver_ids",
    "get_version", "set_log_level", "compare_images",
    # classes
    "Slide", "Scene",
    # conversion parameters
    "SVSJpegParameters", "SVSJp2KParameters",
    "OMETIFFJpegParameters", "OMETIFFJp2KParameters",
    # transformations
    "ColorTransformation", "ColorManagement", "GaussianBlurFilter",
    "MedianBlurFilter", "BilateralFilter", "CannyFilter", "LaplacianFilter",
    "SobelFilter", "ScharrFilter",
    # enums
    "Compression", "DataType", "ColorSpace", "ColorProfileInfo",
    "ColorProfileSource", "ColorTarget", "IccColorSpace", "RenderingIntent",
    "MissingProfilePolicy",
]


class TestPublicExports:

    @pytest.mark.parametrize("name", PUBLIC_NAMES)
    def test_name_is_exported(self, name):
        assert hasattr(slideio, name), f"slideio.{name} is missing"

    def test_version(self):
        assert slideio.get_version() == "2.10.0"

    def test_driver_ids(self):
        expected = {"AFI", "CZI", "DCM", "GDAL", "NDPI", "OMETIFF", "PHTIFF",
                    "QPTIFF", "SCN", "SVS", "VSI", "ZVI"}
        assert set(slideio.get_driver_ids()) == expected


class TestUnexportedTypes:
    """Types returned by public properties that the package does not export."""

    @pytest.mark.xfail(
        strict=True,
        reason="slideio 2.10.0: Slide.metadata_format and Scene.metadata_format "
               "return a MetadataFormat, but the enum is only reachable as "
               "slideio.core.libs.slideiopybind.MetadataFormat, so there is no "
               "public constant to compare a returned value against",
    )
    def test_metadata_format_enum_is_exported(self):
        assert hasattr(slideio, "MetadataFormat")

    def test_metadata_format_values_are_still_usable_by_name(self):
        """Until the enum is exported, comparing by name is the way out."""
        from slideio.core.libs.slideiopybind import MetadataFormat
        assert set(MetadataFormat.__members__) == {
            "None", "Unknown", "XML", "JSON", "TEXT"}
