"""Session-wide fixtures and import ordering for the slideio test suite.

Importing the real slideio package here, before any test module is collected,
makes one thing deterministic: interface/conftest.py registers a MagicMock for
slideio.core.libs.slideiopybind so the pure-Python wrapper layer can be tested
without the compiled extension.  It uses sys.modules.setdefault, so whichever
import happens first wins.  With the real package already imported the stub is a
no-op for every other directory, instead of depending on collection order.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import slideio  # noqa: E402  imported for its side effect on sys.modules

from common.test_tools import image_path, images_root  # noqa: E402


@pytest.fixture(scope="session")
def corpus_root():
    """Root of the shared image corpus."""
    root = images_root()
    if not root:
        pytest.skip("SLIDEIO_IMAGES_PATH is not set")
    return root


@pytest.fixture
def corpus_image():
    """Factory returning the path of a corpus image by format and subpath."""
    return image_path


@pytest.fixture
def opened_slide():
    """Factory opening slides and closing every one of them at teardown."""
    slides = []

    def _open(path, driver):
        slide = slideio.open_slide(path, driver)
        slides.append(slide)
        return slide

    yield _open

    for slide in slides:
        try:
            slide.close()
        except Exception:
            pass
