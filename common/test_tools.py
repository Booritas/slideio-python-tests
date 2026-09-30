from enum import Enum
import os
import numpy as np
import cv2

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ImageDir(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    FULL = "FULL"

class Tools:
    def getImageDirPath(self, subpath, testImageDir):
        return os.environ.get('SLIDEIO_IMAGES_PATH')
    
    def getImageFilePath(self, format, subpath, testImageDir):
        return os.path.join(self.getImageDirPath(subpath, testImageDir), format, subpath)
    
    def isImageTestAvalable(self, testImageDir):
        """True when the shared image corpus is reachable.

        The previous version called getImageDirPath with one argument against
        a two-argument signature, so the bare except turned every call into
        False.  Nothing called it, which is why that stayed invisible.
        """
        path = self.getImageDirPath(None, testImageDir)
        return bool(path) and os.path.exists(path)
        
    def getTestImagePath(self, format, filename):
        return os.path.join(root_path, "images", format, filename)  

def compute_similarity(leftM, rightM):
    left_size = leftM.shape
    right_size = rightM.shape
    if left_size != right_size:
        raise RuntimeError(f"Image sizes for comparison shall be equal. Left image: {left_size}, Right image: {right_size}")
    
    if leftM.ndim != rightM.ndim:
        raise RuntimeError(f"Number of image dimensions for comparison shall be equal. Left image: {leftM.dim}, Right image: {rightM.dim}")

    if leftM.ndim>2 and (leftM.shape[2] != rightM.shape[2]):
        raise RuntimeError(f"Number of image channels for comparison shall be equal. Left image: {leftM.shape[2]}, Right image: {rightM.shape[2]}")

    if leftM.dtype != rightM.dtype:
        #raise RuntimeError(f"Image types for comparison shall be equal. Left image: {leftM.dtype}, Right image: {rightM.dtype}")
        rightM = rightM.astype(leftM.dtype)  # Convert rightM to the type of leftM

    
    leftM = leftM.flatten()
    rightM = rightM.flatten()
        
    max_val = max(np.max(leftM), np.max(rightM))

    diff = cv2.absdiff(leftM, rightM)
    diffd = diff.astype(np.float32) / max_val
    diffd = np.power(diffd, 1.5)
    sum_val = np.sum(diffd)
    similarity = 1.0 - sum_val / (left_size[0] * left_size[1])
    return similarity

def compare_images(left, right):
    if np.array_equal(left, right):
        return 1.0
    return 0.
        

# ---------------------------------------------------------------------------
# Corpus access helpers
# ---------------------------------------------------------------------------
# The shared image corpus is located through SLIDEIO_IMAGES_PATH.  Tests that
# need an image that is not part of every checkout go through image_path() so a
# missing file produces one clear message instead of an opaque RuntimeError from
# the C++ layer.

_FALSE_VALUES = {"0", "false", "no", "off"}


def images_root():
    """Root of the shared image corpus, or None when it is not configured."""
    return os.environ.get('SLIDEIO_IMAGES_PATH')


def skip_missing_images_enabled():
    """Whether a missing image should skip instead of fail.

    Mirrors the convention of the binding repository: only 0, false, no and off
    count as "not set", so an accidental SLIDEIO_SKIP_MISSING_IMAGES=maybe still
    enables skipping rather than silently doing nothing.  CI must leave the
    variable unset so coverage cannot disappear quietly.
    """
    value = os.environ.get('SLIDEIO_SKIP_MISSING_IMAGES')
    if value is None:
        return False
    return value.strip().lower() not in _FALSE_VALUES


def image_path(image_format, subpath):
    """Absolute path of a corpus image, checked for existence.

    Raises unless SLIDEIO_SKIP_MISSING_IMAGES says otherwise, in which case the
    calling test is skipped.
    """
    root = images_root()
    if not root:
        _missing("SLIDEIO_IMAGES_PATH is not set")
    path = os.path.join(root, image_format, subpath)
    if not os.path.exists(path):
        _missing(f"image not found: {path}")
    return path


def _missing(message):
    if skip_missing_images_enabled():
        import pytest
        pytest.skip(message)
    raise FileNotFoundError(message)
