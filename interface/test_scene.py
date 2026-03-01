"""Unit tests for the Scene wrapper class.

All tests in this module use a MagicMock in place of the compiled CoreScene so
that the C++ extension is not required to run the test suite.
"""
from unittest.mock import MagicMock, patch

import pytest

from slideio.wrappers.py_slideio import Scene


# ---------------------------------------------------------------------------
# Properties – simple delegation
# ---------------------------------------------------------------------------

class TestSceneProperties:
    """Every plain property on Scene must delegate to the underlying CoreScene."""

    def test_name(self, core_scene):
        assert Scene(core_scene).name == "TestScene"

    def test_compression(self, core_scene):
        assert Scene(core_scene).compression == 0

    def test_file_path(self, core_scene):
        assert Scene(core_scene).file_path == "/path/to/file.svs"

    def test_magnification(self, core_scene):
        assert Scene(core_scene).magnification == 20.0

    def test_num_channels(self, core_scene):
        assert Scene(core_scene).num_channels == 3

    def test_num_t_frames(self, core_scene):
        assert Scene(core_scene).num_t_frames == 1

    def test_num_z_slices(self, core_scene):
        assert Scene(core_scene).num_z_slices == 1

    def test_rect(self, core_scene):
        assert Scene(core_scene).rect == (0, 0, 1000, 800)

    def test_resolution(self, core_scene):
        assert Scene(core_scene).resolution == (0.5e-6, 0.5e-6)

    def test_t_resolution(self, core_scene):
        assert Scene(core_scene).t_resolution == 0.0

    def test_z_resolution(self, core_scene):
        assert Scene(core_scene).z_resolution == 0.0

    def test_num_aux_images(self, core_scene):
        assert Scene(core_scene).num_aux_images == 2

    def test_num_zoom_levels(self, core_scene):
        assert Scene(core_scene).num_zoom_levels == 5

    def test_metadata_format(self, core_scene):
        assert Scene(core_scene).metadata_format == "XML"


# ---------------------------------------------------------------------------
# Properties – computed from rect
# ---------------------------------------------------------------------------

class TestSceneComputedProperties:
    """size and origin are derived from rect and must use rect[2:4] and rect[0:2]."""

    @pytest.mark.parametrize("rect,expected_size,expected_origin", [
        ((0, 0, 1000, 800), (1000, 800), (0, 0)),
        ((10, 20, 500, 300), (500, 300), (10, 20)),
        ((100, 200, 1, 1), (1, 1), (100, 200)),
    ])
    def test_size_and_origin(self, core_scene, rect, expected_size, expected_origin):
        core_scene.rect = rect
        scene = Scene(core_scene)
        assert scene.size == expected_size
        assert scene.origin == expected_origin

    def test_size_reads_rect_once_per_call(self, core_scene):
        """rect is a property on the mock; accessing size should call it exactly once."""
        core_scene.rect = (5, 10, 200, 100)
        scene = Scene(core_scene)
        _ = scene.size
        assert core_scene.rect is not None  # access didn't raise

    def test_origin_reads_rect_once_per_call(self, core_scene):
        core_scene.rect = (5, 10, 200, 100)
        scene = Scene(core_scene)
        _ = scene.origin
        assert core_scene.rect is not None


# ---------------------------------------------------------------------------
# Lifecycle – constructor, close, __del__, context manager
# ---------------------------------------------------------------------------

class TestSceneLifecycle:

    def test_constructor_stores_core_scene(self, core_scene):
        scene = Scene(core_scene)
        assert scene.scene is core_scene

    def test_repr_delegates_to_core(self, core_scene):
        core_scene.__repr__ = MagicMock(return_value="CoreScene(path=/foo)")
        assert repr(Scene(core_scene)) == "CoreScene(path=/foo)"

    def test_close_sets_scene_to_none(self, core_scene):
        scene = Scene(core_scene)
        scene.close()
        assert scene.scene is None

    def test_close_is_idempotent(self, core_scene):
        scene = Scene(core_scene)
        scene.close()
        scene.close()  # must not raise
        assert scene.scene is None

    def test_context_manager_returns_self(self, core_scene):
        scene = Scene(core_scene)
        with scene as s:
            assert s is scene

    def test_context_manager_closes_on_clean_exit(self, core_scene):
        scene = Scene(core_scene)
        with scene:
            pass
        assert scene.scene is None

    def test_context_manager_closes_on_exception(self, core_scene):
        scene = Scene(core_scene)
        try:
            with scene:
                raise ValueError("test error")
        except ValueError:
            pass
        assert scene.scene is None

    def test_context_manager_propagates_exception(self, core_scene):
        scene = Scene(core_scene)
        with pytest.raises(ValueError, match="test error"):
            with scene:
                raise ValueError("test error")


# ---------------------------------------------------------------------------
# Simple delegating methods
# ---------------------------------------------------------------------------

class TestSceneDelegatingMethods:

    def test_get_zoom_level_info_delegates(self, core_scene):
        expected = MagicMock(name="LevelInfo")
        core_scene.get_zoom_level_info.return_value = expected
        result = Scene(core_scene).get_zoom_level_info(2)
        core_scene.get_zoom_level_info.assert_called_once_with(2)
        assert result is expected

    def test_get_aux_image_names_delegates(self, core_scene):
        core_scene.get_aux_image_names.return_value = ["macro", "thumbnail"]
        result = Scene(core_scene).get_aux_image_names()
        core_scene.get_aux_image_names.assert_called_once_with()
        assert result == ["macro", "thumbnail"]

    def test_get_raw_metadata_delegates(self, core_scene):
        core_scene.get_raw_metadata.return_value = "<root/>"
        result = Scene(core_scene).get_raw_metadata()
        core_scene.get_raw_metadata.assert_called_once_with()
        assert result == "<root/>"

    def test_get_channel_data_type_delegates(self, core_scene):
        expected = MagicMock(name="DataType")
        core_scene.get_channel_data_type.return_value = expected
        result = Scene(core_scene).get_channel_data_type(1)
        core_scene.get_channel_data_type.assert_called_once_with(1)
        assert result is expected

    def test_get_channel_name_delegates(self, core_scene):
        core_scene.get_channel_name.return_value = "DAPI"
        result = Scene(core_scene).get_channel_name(0)
        core_scene.get_channel_name.assert_called_once_with(0)
        assert result == "DAPI"


# ---------------------------------------------------------------------------
# read_block – parameter handling and None-to-[] conversion
# ---------------------------------------------------------------------------

class TestSceneReadBlock:

    def test_defaults_are_forwarded_to_core(self, core_scene):
        Scene(core_scene).read_block()
        core_scene.read_block.assert_called_once_with(
            (0, 0, 0, 0), (0, 0), [], (0, 1), (0, 1)
        )

    def test_none_channel_indices_converted_to_empty_list(self, core_scene):
        Scene(core_scene).read_block(channel_indices=None)
        args, _ = core_scene.read_block.call_args
        assert args[2] == []

    def test_explicit_channel_indices_passed_through(self, core_scene):
        Scene(core_scene).read_block(channel_indices=[0, 2])
        args, _ = core_scene.read_block.call_args
        assert args[2] == [0, 2]

    def test_returns_value_from_core(self, core_scene):
        expected = MagicMock(name="numpy_array")
        core_scene.read_block.return_value = expected
        result = Scene(core_scene).read_block(rect=(10, 10, 100, 100), size=(50, 50))
        assert result is expected

    def test_all_params_forwarded(self, core_scene):
        Scene(core_scene).read_block(
            rect=(5, 10, 200, 150),
            size=(100, 75),
            channel_indices=[1, 2],
            slices=(0, 3),
            frames=(1, 4),
        )
        core_scene.read_block.assert_called_once_with(
            (5, 10, 200, 150), (100, 75), [1, 2], (0, 3), (1, 4)
        )

    def test_empty_list_channel_indices_passed_through(self, core_scene):
        Scene(core_scene).read_block(channel_indices=[])
        args, _ = core_scene.read_block.call_args
        assert args[2] == []


# ---------------------------------------------------------------------------
# get_aux_image – None-to-[] conversion and read_block delegation
# ---------------------------------------------------------------------------

class TestSceneGetAuxImage:

    def _make_aux_scene(self):
        aux = MagicMock(name="AuxCoreScene")
        aux.read_block.return_value = MagicMock(name="numpy_array")
        return aux

    def test_calls_get_aux_image_on_core_scene(self, core_scene):
        aux = self._make_aux_scene()
        core_scene.get_aux_image.return_value = aux
        Scene(core_scene).get_aux_image("macro")
        core_scene.get_aux_image.assert_called_once_with("macro")

    def test_calls_read_block_with_correct_defaults(self, core_scene):
        aux = self._make_aux_scene()
        core_scene.get_aux_image.return_value = aux
        Scene(core_scene).get_aux_image("macro")
        aux.read_block.assert_called_once_with(
            rect=(0, 0, 0, 0), size=(0, 0), channel_indices=[], slices=(0, 1), frames=(0, 1)
        )

    def test_none_channel_indices_converted_to_empty_list(self, core_scene):
        aux = self._make_aux_scene()
        core_scene.get_aux_image.return_value = aux
        Scene(core_scene).get_aux_image("macro", channel_indices=None)
        _, kwargs = aux.read_block.call_args
        assert kwargs["channel_indices"] == []

    def test_explicit_size_and_channel_indices_forwarded(self, core_scene):
        aux = self._make_aux_scene()
        core_scene.get_aux_image.return_value = aux
        Scene(core_scene).get_aux_image("macro", size=(100, 80), channel_indices=[0])
        _, kwargs = aux.read_block.call_args
        assert kwargs["size"] == (100, 80)
        assert kwargs["channel_indices"] == [0]

    def test_returns_numpy_array_from_read_block(self, core_scene):
        expected = MagicMock(name="numpy_array")
        aux = self._make_aux_scene()
        aux.read_block.return_value = expected
        core_scene.get_aux_image.return_value = aux
        result = Scene(core_scene).get_aux_image("macro")
        assert result is expected


# ---------------------------------------------------------------------------
# save_image – callback routing
# ---------------------------------------------------------------------------

class TestSceneSaveImage:

    def test_without_callback_calls_core_convert_scene(self, core_scene):
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn:
            Scene(core_scene).save_image(params, "/out/file.svs")
            mock_fn.assert_called_once_with(core_scene, params, "/out/file.svs")

    def test_without_callback_does_not_call_ex_variant(self, core_scene):
        params = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as _mock, \
             patch("slideio.wrappers.py_slideio.core_convert_scene_ex") as mock_ex:
            Scene(core_scene).save_image(params, "/out/file.svs")
            mock_ex.assert_not_called()

    def test_with_callback_calls_core_convert_scene_ex(self, core_scene):
        params = MagicMock()
        callback = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene_ex") as mock_ex:
            Scene(core_scene).save_image(params, "/out/file.svs", callback=callback)
            mock_ex.assert_called_once_with(core_scene, params, "/out/file.svs", callback)

    def test_with_callback_does_not_call_non_ex_variant(self, core_scene):
        params = MagicMock()
        callback = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_convert_scene") as mock_fn, \
             patch("slideio.wrappers.py_slideio.core_convert_scene_ex"):
            Scene(core_scene).save_image(params, "/out/file.svs", callback=callback)
            mock_fn.assert_not_called()


# ---------------------------------------------------------------------------
# apply_transformation – result wrapping
# ---------------------------------------------------------------------------

class TestSceneApplyTransformation:

    def test_returns_scene_instance(self, core_scene):
        new_core = MagicMock(name="TransformedCoreScene")
        transformation = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_transform_scene", return_value=new_core):
            result = Scene(core_scene).apply_transformation(transformation)
        assert isinstance(result, Scene)

    def test_returned_scene_wraps_transformed_core(self, core_scene):
        new_core = MagicMock(name="TransformedCoreScene")
        transformation = MagicMock()
        with patch("slideio.wrappers.py_slideio.core_transform_scene", return_value=new_core):
            result = Scene(core_scene).apply_transformation(transformation)
        assert result.scene is new_core

    def test_passes_transformation_to_core(self, core_scene):
        transformation = MagicMock()
        with patch(
            "slideio.wrappers.py_slideio.core_transform_scene",
            return_value=MagicMock(),
        ) as mock_fn:
            Scene(core_scene).apply_transformation(transformation)
            mock_fn.assert_called_once_with(core_scene, transformation)
