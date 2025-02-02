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
        if testImageDir == ImageDir.PUBLIC:
            return os.environ.get('SLIDEIO_TEST_DATA_PATH')
        elif testImageDir == ImageDir.PRIVATE:
            return os.environ.get('SLIDEIO_TEST_DATA_PRIV_PATH')
        elif testImageDir == ImageDir.FULL:
            return os.environ.get('SLIDEIO_IMAGES_PATH')
        raise Exception("Invalid test image directory")
    
    def getImageFilePath(self, format, subpath, testImageDir):
        return os.path.join(self.getImageDirPath(subpath, testImageDir), format, subpath)
    
    def isImageTestAvalable(self, testImageDir):
        try:
            return os.path.exists(self.getImageDirPath(testImageDir))
        except:
            return False
        
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
        