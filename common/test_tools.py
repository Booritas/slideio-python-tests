from enum import Enum
import os
import numpy as np

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


def compare_images(left, right):
    if np.array_equal(left, right):
        return 1.0
    return 0.
        