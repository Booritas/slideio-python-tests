"""Unit tests for module-level functions in slideio/wrappers/py_slideio.py."""
from unittest.mock import MagicMock, patch

import pytest

from slideio.wrappers.py_slideio import (
    Scene,
    Slide,
    compare_images,
    convert_scene,
    get_driver_ids,
    get_version,
    open_slide,
    set_log_level,
    transform_scene,
)


# ---------------------------------------------------------------------------
# open_slide
# ---------------------------------------------------------------------------

class TestOpenSlide:

    def test_returns_slide_instance(self, core_slide):
        with patch("slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide):
            result = open_slide("/path/to/file.svs")
        assert isinstance(result, Slide)

    def test_default_driver_is_auto(self, core_slide):
        with patch(
            "slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide
        ) as mock_open:
            open_slide("/path/to/file.svs")
            mock_open.assert_called_once_with("/path/to/file.svs", "AUTO")

    def test_explicit_driver_forwarded(self, core_slide):
        with patch(
            "slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide
        ) as mock_open:
            open_slide("/path/to/file.svs", driver="CZI")
            mock_open.assert_called_once_with("/path/to/file.svs", "CZI")

    @pytest.mark.parametrize("driver", ["SVS", "CZI", "GDAL", "NDPI", "AUTO"])
    def test_various_drivers_forwarded(self, core_slide, driver):
        with patch(
            "slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide
        ) as mock_open:
            open_slide("/some/file.svs", driver=driver)
            mock_open.assert_called_once_with("/some/file.svs", driver)

    def test_slide_wraps_returned_core_slide(self, core_slide):
        with patch("slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide):
            slide = open_slide("/path/to/file.svs")
        assert slide.slide is core_slide


# ---------------------------------------------------------------------------
# get_driver_ids
# ---------------------------------------------------------------------------

class TestGetDriverIds:

    def test_delegates_to_core(self):
        expected = ["SVS", "CZI", "GDAL", "NDPI"]
        with patch(
            "slideio.wrappers.py_slideio.core_get_driver_ids", return_value=expected
        ) as mock_fn:
            result = get_driver_ids()
            mock_fn.assert_called_once_with()
            assert result == expected

    def test_returns_core_result_unchanged(self):
        ids = ["DRIVER_A", "DRIVER_B"]
        with patch("slideio.wrappers.py_slideio.core_get_driver_ids", return_value=ids):
            assert get_driver_ids() is ids


# ---------------------------------------------------------------------------
# set_log_level
# ---------------------------------------------------------------------------

class TestSetLogLevel:

    def test_delegates_to_core(self):
        with patch("slideio.wrappers.py_slideio.core_set_log_level") as mock_fn:
            set_log_level("WARNING")
            mock_fn.assert_called_once_with("WARNING")

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_various_levels_forwarded(self, level):
        with patch("slideio.wrappers.py_slideio.core_set_log_level") as mock_fn:
            set_log_level(level)
            mock_fn.assert_called_once_with(level)


# ---------------------------------------------------------------------------
# get_version
# ---------------------------------------------------------------------------

class TestGetVersion:

    def test_delegates_to_core(self):
        with patch(
            "slideio.wrappers.py_slideio.core_get_version", return_value="2.8.0"
        ) as mock_fn:
            result = get_version()
            mock_fn.assert_called_once_with()
            assert result == "2.8.0"

    def test_returns_core_result_unchanged(self):
        with patch("slideio.wrappers.py_slideio.core_get_version", return_value="1.2.3"):
            assert get_version() == "1.2.3"


# ---------------------------------------------------------------------------
# compare_images
# ---------------------------------------------------------------------------

class TestCompareImages:

    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            compare_images(MagicMock(), MagicMock())

    def test_error_message_mentions_function_name(self):
        with pytest.raises(NotImplementedError, match="compare_images"):
            compare_images(MagicMock(), MagicMock())


# ---------------------------------------------------------------------------
# convert_scene
# ---------------------------------------------------------------------------

class TestConvertScene:

    def test_without_callback_calls_core_convert_scene(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn:
            convert_scene(scene, params, "/output/file.svs")
            mock_fn.assert_called_once_with(core_scene, params, "/output/file.svs")

    def test_without_callback_does_not_call_ex_variant(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene"), \
             patch("slideio.wrappers.py_slideio.core_convert_scene_ex") as mock_ex:
            convert_scene(scene, params, "/output/file.svs")
            mock_ex.assert_not_called()

    def test_none_callback_uses_non_ex_variant(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn, \
             patch("slideio.wrappers.py_slideio.core_convert_scene_ex") as mock_ex:
            convert_scene(scene, params, "/output/file.svs", callback=None)
            mock_fn.assert_called_once()
            mock_ex.assert_not_called()

    def test_with_callback_calls_core_convert_scene_ex(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        callback = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene_ex") as mock_ex:
            convert_scene(scene, params, "/output/file.svs", callback=callback)
            mock_ex.assert_called_once_with(core_scene, params, "/output/file.svs", callback)

    def test_with_callback_does_not_call_non_ex_variant(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        callback = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn, \
             patch("slideio.wrappers.py_slideio.core_convert_scene_ex"):
            convert_scene(scene, params, "/output/file.svs", callback=callback)
            mock_fn.assert_not_called()

    def test_passes_inner_core_scene_not_wrapper(self, core_scene):
        """convert_scene must pass scene.scene (CoreScene), not the Scene wrapper."""
        scene = Scene(core_scene)
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn:
            convert_scene(scene, params, "/output/file.svs")
            args, _ = mock_fn.call_args
            assert args[0] is core_scene


# ---------------------------------------------------------------------------
# transform_scene
# ---------------------------------------------------------------------------

class TestTransformScene:

    def test_returns_scene_instance(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        with patch(
            "slideio.wrappers.py_slideio.core_transform_scene",
            return_value=MagicMock(name="TransformedCore"),
        ):
            result = transform_scene(scene, params)
        assert isinstance(result, Scene)

    def test_returned_scene_wraps_transformed_core(self, core_scene):
        scene = Scene(core_scene)
        new_core = MagicMock(name="TransformedCoreScene")
        params = MagicMock()
        with patch(
            "slideio.wrappers.py_slideio.core_transform_scene", return_value=new_core
        ):
            result = transform_scene(scene, params)
        assert result.scene is new_core

    def test_passes_inner_core_scene_to_transform(self, core_scene):
        """transform_scene must pass scene.scene (CoreScene), not the wrapper."""
        scene = Scene(core_scene)
        params = MagicMock()
        with patch(
            "slideio.wrappers.py_slideio.core_transform_scene",
            return_value=MagicMock(),
        ) as mock_fn:
            transform_scene(scene, params)
            args, _ = mock_fn.call_args
            assert args[0] is core_scene

    def test_passes_params_to_transform(self, core_scene):
        scene = Scene(core_scene)
        params = MagicMock()
        with patch(
            "slideio.wrappers.py_slideio.core_transform_scene",
            return_value=MagicMock(),
        ) as mock_fn:
            transform_scene(scene, params)
            args, _ = mock_fn.call_args
            assert args[1] is params
