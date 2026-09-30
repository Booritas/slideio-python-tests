"""The public surface of the slideio package.

The binding has three layers: the compiled slideiopybind module, the raw import
layer in slideio.core, and the public wrappers re-exported from slideio.  A type
that a public property hands back should be reachable from the public package,
otherwise callers have to import the private extension module to compare against
it.  These tests pin what 2.10 exports.
"""
import pytest
import slideio

from common.test_tools import image_path

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
    "MissingProfilePolicy", "MetadataFormat", "TransformationType",
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


class TestEnumsReturnedByProperties:
    """A type a public property returns must be reachable from the package.

    Both of these were registered in the binding but unreachable from slideio
    itself, so a caller could not compare a returned value to a constant
    without importing the private extension module.
    """

    def test_metadata_format_enum_is_exported(self):
        assert hasattr(slideio, "MetadataFormat")

    def test_metadata_format_members(self):
        assert set(slideio.MetadataFormat.__members__) == {
            "None", "Unknown", "XML", "JSON", "TEXT"}

    def test_metadata_format_compares_against_the_public_constant(self):
        path = image_path("philips", "Philips-1.tiff")
        slide = slideio.open_slide(path, "PHTIFF")
        try:
            assert slide.metadata_format == slideio.MetadataFormat.XML
        finally:
            slide.close()

    def test_transformation_type_enum_is_exported(self):
        assert hasattr(slideio, "TransformationType")

    def test_transformation_type_members(self):
        assert set(slideio.TransformationType.__members__) == {
            "Unknown", "ColorTransformation", "ColorManagement",
            "GaussianBlurFilter", "MedianBlurFilter", "SobelFilter",
            "ScharrFilter", "LaplacianFilter", "BilateralFilter", "CannyFilter"}
