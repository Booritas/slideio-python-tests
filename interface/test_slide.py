"""Unit tests for the Slide wrapper class.

All tests use a MagicMock in place of the compiled CoreSlide so that the
C++ extension is not required to run the suite.
"""
from unittest.mock import MagicMock, patch

import pytest

from slideio.wrappers.py_slideio import Scene, Slide


# ---------------------------------------------------------------------------
# Helper: create a Slide with a mocked CoreSlide
# ---------------------------------------------------------------------------

def _make_slide(core_slide_mock):
    """Return a Slide whose internal CoreSlide is *core_slide_mock*."""
    with patch("slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide_mock):
        return Slide("/path/to/file.svs", "AUTO")


# ---------------------------------------------------------------------------
# Properties – simple delegation
# ---------------------------------------------------------------------------

class TestSlideProperties:

    def test_num_scenes(self, core_slide):
        assert _make_slide(core_slide).num_scenes == 2

    def test_raw_metadata(self, core_slide):
        assert _make_slide(core_slide).raw_metadata == "<xml/>"

    def test_metadata_format(self, core_slide):
        assert _make_slide(core_slide).metadata_format == "XML"

    def test_file_path(self, core_slide):
        assert _make_slide(core_slide).file_path == "/path/to/file.svs"

    def test_num_aux_images(self, core_slide):
        assert _make_slide(core_slide).num_aux_images == 1


# ---------------------------------------------------------------------------
# Lifecycle – constructor, close, context manager
# ---------------------------------------------------------------------------

class TestSlideLifecycle:

    def test_constructor_calls_core_open_slide_with_given_args(self, core_slide):
        with patch(
            "slideio.wrappers.py_slideio.core_open_slide", return_value=core_slide
        ) as mock_open:
            Slide("/path/to/file.svs", "SVS")
            mock_open.assert_called_once_with("/path/to/file.svs", "SVS")

    def test_constructor_stores_core_slide(self, core_slide):
        slide = _make_slide(core_slide)
        assert slide.slide is core_slide

    def test_repr_delegates_to_core(self, core_slide):
        core_slide.__repr__ = MagicMock(return_value="CoreSlide(file=/foo)")
        slide = _make_slide(core_slide)
        assert repr(slide) == "CoreSlide(file=/foo)"

    def test_close_sets_slide_to_none(self, core_slide):
        slide = _make_slide(core_slide)
        slide.close()
        assert slide.slide is None

    def test_close_is_idempotent(self, core_slide):
        slide = _make_slide(core_slide)
        slide.close()
        slide.close()  # must not raise
        assert slide.slide is None

    def test_context_manager_returns_self(self, core_slide):
        slide = _make_slide(core_slide)
        with slide as s:
            assert s is slide

    def test_context_manager_closes_on_clean_exit(self, core_slide):
        slide = _make_slide(core_slide)
        with slide:
            pass
        assert slide.slide is None

    def test_context_manager_closes_on_exception(self, core_slide):
        slide = _make_slide(core_slide)
        try:
            with slide:
                raise RuntimeError("test")
        except RuntimeError:
            pass
        assert slide.slide is None

    def test_context_manager_propagates_exception(self, core_slide):
        slide = _make_slide(core_slide)
        with pytest.raises(RuntimeError, match="test"):
            with slide:
                raise RuntimeError("test")


# ---------------------------------------------------------------------------
# get_scene / get_scene_by_name
# ---------------------------------------------------------------------------

class TestSlideGetScene:

    def test_get_scene_returns_scene_wrapper(self, core_slide, core_scene):
        core_slide.get_scene.return_value = core_scene
        slide = _make_slide(core_slide)
        result = slide.get_scene(0)
        core_slide.get_scene.assert_called_once_with(0)
        assert isinstance(result, Scene)

    def test_get_scene_wraps_correct_core_scene(self, core_slide, core_scene):
        core_slide.get_scene.return_value = core_scene
        result = _make_slide(core_slide).get_scene(1)
        assert result.scene is core_scene

    @pytest.mark.parametrize("index", [0, 1, 5])
    def test_get_scene_forwards_index(self, core_slide, core_scene, index):
        core_slide.get_scene.return_value = core_scene
        _make_slide(core_slide).get_scene(index)
        core_slide.get_scene.assert_called_once_with(index)

    def test_get_scene_by_name_returns_scene_wrapper(self, core_slide, core_scene):
        core_slide.get_scene_by_name.return_value = core_scene
        result = _make_slide(core_slide).get_scene_by_name("Scene0")
        core_slide.get_scene_by_name.assert_called_once_with("Scene0")
        assert isinstance(result, Scene)

    def test_get_scene_by_name_wraps_correct_core_scene(self, core_slide, core_scene):
        core_slide.get_scene_by_name.return_value = core_scene
        result = _make_slide(core_slide).get_scene_by_name("Scene0")
        assert result.scene is core_scene


# ---------------------------------------------------------------------------
# Auxiliary image methods
# ---------------------------------------------------------------------------

class TestSlideAuxImages:

    def test_get_aux_image_returns_scene_wrapper(self, core_slide, core_scene):
        core_slide.get_aux_image.return_value = core_scene
        result = _make_slide(core_slide).get_aux_image("macro")
        core_slide.get_aux_image.assert_called_once_with("macro")
        assert isinstance(result, Scene)

    def test_get_aux_image_wraps_correct_core_scene(self, core_slide, core_scene):
        core_slide.get_aux_image.return_value = core_scene
        result = _make_slide(core_slide).get_aux_image("macro")
        assert result.scene is core_scene

    def test_get_aux_image_names_delegates(self, core_slide):
        core_slide.get_aux_image_names.return_value = ["macro", "label"]
        result = _make_slide(core_slide).get_aux_image_names()
        core_slide.get_aux_image_names.assert_called_once_with()
        assert result == ["macro", "label"]

    # --- get_aux_image_raster ---

    def _make_aux_core_scene(self):
        aux = MagicMock(name="AuxCoreScene")
        aux.read_block.return_value = MagicMock(name="numpy_array")
        return aux

    def test_get_aux_image_raster_returns_array_from_read_block(self, core_slide):
        aux = self._make_aux_core_scene()
        expected = MagicMock(name="numpy_array")
        aux.read_block.return_value = expected
        core_slide.get_aux_image.return_value = aux
        result = _make_slide(core_slide).get_aux_image_raster("macro")
        assert result is expected

    def test_get_aux_image_raster_calls_read_block_with_defaults(self, core_slide):
        aux = self._make_aux_core_scene()
        core_slide.get_aux_image.return_value = aux
        _make_slide(core_slide).get_aux_image_raster("macro")
        aux.read_block.assert_called_once_with(
            rect=(0, 0, 0, 0), size=(0, 0), channel_indices=[], slices=(0, 1), frames=(0, 1)
        )

    def test_get_aux_image_raster_none_channel_indices_converted_to_empty(self, core_slide):
        aux = self._make_aux_core_scene()
        core_slide.get_aux_image.return_value = aux
        _make_slide(core_slide).get_aux_image_raster("macro", channel_indices=None)
        _, kwargs = aux.read_block.call_args
        assert kwargs["channel_indices"] == []

    def test_get_aux_image_raster_explicit_size_forwarded(self, core_slide):
        aux = self._make_aux_core_scene()
        core_slide.get_aux_image.return_value = aux
        _make_slide(core_slide).get_aux_image_raster("macro", size=(200, 150))
        _, kwargs = aux.read_block.call_args
        assert kwargs["size"] == (200, 150)

    def test_get_aux_image_raster_explicit_channel_indices_forwarded(self, core_slide):
        aux = self._make_aux_core_scene()
        core_slide.get_aux_image.return_value = aux
        _make_slide(core_slide).get_aux_image_raster("macro", channel_indices=[0, 1])
        _, kwargs = aux.read_block.call_args
        assert kwargs["channel_indices"] == [0, 1]

    def test_get_aux_image_raster_fetches_correct_image(self, core_slide):
        aux = self._make_aux_core_scene()
        core_slide.get_aux_image.return_value = aux
        _make_slide(core_slide).get_aux_image_raster("thumbnail")
        core_slide.get_aux_image.assert_called_once_with("thumbnail")
