"""Shared test fixtures and sys.modules mocking for unit tests.

slideio.core.libs.slideiopybind is a compiled C++ extension that may not be
available in all test environments.  This conftest stubs it out *before* any
slideio sub-package is imported so the pure-Python wrapper layer can be
exercised in isolation.
"""
import sys
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# C++ extension stub
# ---------------------------------------------------------------------------
# Must be registered before any slideio sub-package is imported.
_pybind_stub = MagicMock(name="slideio.core.libs.slideiopybind")
sys.modules.setdefault("slideio.core.libs", MagicMock(name="slideio.core.libs"))
sys.modules.setdefault("slideio.core.libs.slideiopybind", _pybind_stub)


# ---------------------------------------------------------------------------
# Reusable mock factories
# ---------------------------------------------------------------------------

@pytest.fixture
def core_scene():
    """MagicMock pre-configured to behave like a CoreScene object."""
    mock = MagicMock(name="CoreScene")
    mock.name = "TestScene"
    mock.compression = 0
    mock.file_path = "/path/to/file.svs"
    mock.magnification = 20.0
    mock.num_channels = 3
    mock.num_t_frames = 1
    mock.num_z_slices = 1
    mock.rect = (0, 0, 1000, 800)
    mock.resolution = (0.5e-6, 0.5e-6)
    mock.t_resolution = 0.0
    mock.z_resolution = 0.0
    mock.num_aux_images = 2
    mock.num_zoom_levels = 5
    mock.metadata_format = "XML"
    return mock


@pytest.fixture
def core_slide():
    """MagicMock pre-configured to behave like a CoreSlide object."""
    mock = MagicMock(name="CoreSlide")
    mock.num_scenes = 2
    mock.raw_metadata = "<xml/>"
    mock.metadata_format = "XML"
    mock.file_path = "/path/to/file.svs"
    mock.num_aux_images = 1
    return mock
