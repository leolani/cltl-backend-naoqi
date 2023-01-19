import unittest

import numpy as np

from cltl.naoqi.image_source import NAOqiCameraIndex, CameraResolution, NAOqiCamera


class DummySession:
    def service(self, name):
        return DummyService()

    def registerService(self, name, cls):
        pass


class DummyService:
    def hasDepthCamera(self):
        return True

    def setClientPreferences(self, cls, rate, index, _):
        pass

    def subscribeCameras(self, *args, **kwargs):
        pass

    def unsubscribe(self, *args, **kwargs):
        pass

    def getImagesRemote(self, *args, **kwargs):
        width, height = CameraResolution.QQQVGA.value
        data = np.ones((CameraResolution.QQQVGA.value[1], CameraResolution.QQQVGA.value[0], 3,), dtype=np.uint8)
        camera = NAOqiCameraIndex.TOP
        left, top, right, bottom = (0, 0) + CameraResolution.QQQVGA.value

        return [(width, height, None, None, None, None, data, camera, left, top, right, bottom)]

    def getAngles(self, *args, **kwargs):
        return 0, 0


class NAOqiImageSourceTest(unittest.TestCase):
    def test_source(self):
        cam = NAOqiCamera(DummySession(), CameraResolution.QQQVGA, 0.001)

        with cam as source:
            image = source.capture()

        self.assertEquals(CameraResolution.QQQVGA.value[::-1] + (3,), image.image.shape)


if __name__ == '__main__':
    unittest.main()