"""The ColorManagement transformation, introduced in slideio 2.10.

ColorManagement converts a scene's pixels from its embedded ICC profile into a
chosen colorimetric target.  These tests cover what the Python caller controls:
the parameter defaults, that each target actually changes the pixels and in the
documented numeric type, and how a scene with no profile behaves under each
MissingProfilePolicy.
"""
import numpy as np
import pytest
import slideio

from common.test_tools import image_path

# A region of the Aperio slide that carries an embedded ScanScope profile, and
# one of the same driver's unprofiled slide.  Both are small reads: the point is
# the colour pipeline, not throughput.
PROFILED = ("SVS", "svs", "JP2K-33003-1.svs", (1000, 1000, 256, 256))
UNPROFILED = ("SVS", "svs", "CMU-1-Small-Region.svs", (500, 500, 256, 256))
BLOCK_SIZE = (64, 64)

# Each target and the raster dtype it produces.  sRGB stays in the scene's 8 bit
# domain; the colorimetric targets are floating point.
TARGET_DTYPES = {
    slideio.ColorTarget.SRGB: np.uint8,
    slideio.ColorTarget.LAB: np.float32,
    slideio.ColorTarget.XYZ: np.float32,
    slideio.ColorTarget.LINEAR_RGB: np.float32,
}


@pytest.fixture
def profiled_scene(opened_slide):
    driver, fmt, subpath, _ = PROFILED
    return opened_slide(image_path(fmt, subpath), driver).get_scene(0)


@pytest.fixture
def unprofiled_scene(opened_slide):
    driver, fmt, subpath, _ = UNPROFILED
    return opened_slide(image_path(fmt, subpath), driver).get_scene(0)


def read(scene, rect):
    return scene.read_block(rect=rect, size=BLOCK_SIZE)


def transformed(scene, rect, **params):
    management = slideio.ColorManagement()
    for name, value in params.items():
        setattr(management, name, value)
    return read(scene.apply_transformation([management]), rect)


class TestParameterDefaults:
    """A default-constructed ColorManagement carries documented defaults."""

    def test_defaults(self):
        management = slideio.ColorManagement()
        assert management.target == slideio.ColorTarget.SRGB
        assert management.intent == slideio.RenderingIntent.RELATIVE_COLORIMETRIC
        assert management.black_point_compensation is True
        assert management.missing_profile_policy == slideio.MissingProfilePolicy.ASSUME_SRGB
        assert management.source_profile_override is None

    @pytest.mark.parametrize("target", sorted(TARGET_DTYPES, key=lambda t: t.name))
    def test_target_round_trips(self, target):
        management = slideio.ColorManagement()
        management.target = target
        assert management.target == target

    @pytest.mark.parametrize("intent", sorted(slideio.RenderingIntent.__members__.values(), key=lambda i: i.name))
    def test_intent_round_trips(self, intent):
        management = slideio.ColorManagement()
        management.intent = intent
        assert management.intent == intent

    @pytest.mark.parametrize("enabled", [True, False])
    def test_black_point_compensation_round_trips(self, enabled):
        management = slideio.ColorManagement()
        management.black_point_compensation = enabled
        assert management.black_point_compensation is enabled

    def test_transformation_type_is_readable(self):
        """Reading .type raised until TransformationType was registered."""
        assert slideio.ColorManagement().type == slideio.TransformationType.ColorManagement

    def test_every_transformation_reports_its_own_type(self):
        """Each wrapper must name itself, not inherit a neighbour's type."""
        for name in ("ColorTransformation", "ColorManagement",
                     "GaussianBlurFilter", "MedianBlurFilter", "SobelFilter",
                     "ScharrFilter", "LaplacianFilter", "BilateralFilter",
                     "CannyFilter"):
            transformation = getattr(slideio, name)()
            assert transformation.type == getattr(slideio.TransformationType, name)


class TestProfiledScene:
    """Converting a scene that carries an embedded profile."""

    def test_transformation_changes_pixels(self, profiled_scene):
        _, _, _, rect = PROFILED
        assert not np.array_equal(transformed(profiled_scene, rect), read(profiled_scene, rect))

    @pytest.mark.parametrize("target", sorted(TARGET_DTYPES, key=lambda t: t.name))
    def test_target_determines_raster_dtype(self, target, profiled_scene):
        _, _, _, rect = PROFILED
        raster = transformed(profiled_scene, rect, target=target)
        assert raster.dtype == TARGET_DTYPES[target]
        assert raster.shape == (BLOCK_SIZE[1], BLOCK_SIZE[0], 3)

    def test_every_target_produces_a_distinct_raster(self, profiled_scene):
        """No two targets may collapse onto the same pixels."""
        _, _, _, rect = PROFILED
        targets = sorted(TARGET_DTYPES, key=lambda t: t.name)
        rasters = {t: transformed(profiled_scene, rect, target=t) for t in targets}
        for index, left in enumerate(targets):
            for right in targets[index + 1:]:
                a, b = rasters[left], rasters[right]
                assert not (a.shape == b.shape and a.dtype == b.dtype
                            and np.array_equal(a, b)), f"{left} and {right} agree"

    def test_absolute_colorimetric_differs_from_relative(self, profiled_scene):
        """Absolute colorimetric keeps the source white point, so it must differ.

        Perceptual and saturation are free to coincide with relative
        colorimetric when a profile supplies no separate tables for them, so
        only the absolute intent is asserted to differ.
        """
        _, _, _, rect = PROFILED
        relative = transformed(profiled_scene, rect,
                               intent=slideio.RenderingIntent.RELATIVE_COLORIMETRIC)
        absolute = transformed(profiled_scene, rect,
                               intent=slideio.RenderingIntent.ABSOLUTE_COLORIMETRIC)
        assert not np.array_equal(relative, absolute)

    def test_transformed_scene_keeps_geometry(self, profiled_scene):
        management = slideio.ColorManagement()
        scene = profiled_scene.apply_transformation([management])
        assert scene.size == profiled_scene.size
        assert scene.rect == profiled_scene.rect
        assert scene.num_channels == profiled_scene.num_channels


class TestMissingProfilePolicy:
    """A scene with no embedded profile, under each policy."""

    @pytest.mark.parametrize("policy", [
        slideio.MissingProfilePolicy.PASS_THROUGH,
        slideio.MissingProfilePolicy.ASSUME_SRGB,
    ])
    def test_tolerant_policies_leave_pixels_untouched(self, policy, unprofiled_scene):
        """Both tolerant policies are no-ops when the target is already sRGB."""
        _, _, _, rect = UNPROFILED
        result = transformed(unprofiled_scene, rect, missing_profile_policy=policy)
        assert np.array_equal(result, read(unprofiled_scene, rect))

    def test_fail_policy_raises(self, unprofiled_scene):
        _, _, _, rect = UNPROFILED
        with pytest.raises(RuntimeError):
            transformed(unprofiled_scene, rect,
                        missing_profile_policy=slideio.MissingProfilePolicy.FAIL)


class TestEnumCompleteness:
    """The colour enums exposed to Python carry every documented member."""

    @pytest.mark.parametrize("enum_type,names", [
        (slideio.ColorTarget, {"SRGB", "LAB", "XYZ", "LINEAR_RGB"}),
        (slideio.RenderingIntent, {"PERCEPTUAL", "RELATIVE_COLORIMETRIC",
                                   "SATURATION", "ABSOLUTE_COLORIMETRIC"}),
        (slideio.MissingProfilePolicy, {"FAIL", "ASSUME_SRGB", "PASS_THROUGH"}),
        (slideio.ColorProfileSource, {"NONE", "EMBEDDED", "ASSUMED", "SUPPLIED"}),
        (slideio.IccColorSpace, {"UNKNOWN", "RGB", "GRAY", "CMYK", "LAB", "XYZ", "YCBCR"}),
    ])
    def test_members(self, enum_type, names):
        assert set(enum_type.__members__) == names
