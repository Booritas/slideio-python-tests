from enum import Enum
import os

class TestImageDir(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    FULL = "FULL"

class TestTools:
    def getImageTestDirPath(self, subpath, testImageDir):
        if testImageDir == TestImageDir.PUBLIC:
            return os.environ.get('SLIDEIO_TEST_DATA_PATH')
        elif testImageDir == TestImageDir.PRIVATE:
            return os.environ.get('SLIDEIO_TEST_DATA_PRIV_PATH')
        elif testImageDir == TestImageDir.FULL:
            return os.environ.get('SLIDEIO_IMAGES_PATH')
        raise Exception("Invalid test image directory")
    
    def getImageTestFilePath(self, format, subpath, testImageDir):
        return os.path.join(self.getImageTestDirPath(subpath, testImageDir), format, subpath)
    
    def isImageTestAvalable(self, testImageDir):
        try:
            return os.path.exists(self.getImageTestDirPath(testImageDir))
        except:
            return False
