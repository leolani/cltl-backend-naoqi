import enum
import logging
import uuid

import numpy as np
import qi
from cltl.naoqi.api.camera import Image, Bounds, CameraResolution
from cltl.naoqi.spi.image import ImageSource

logger = logging.getLogger(__name__)


# See http://doc.aldebaran.com/2-5/naoqi/vision/alvideodevice.html?highlight=alvideodevice
class NAOqiCameraIndex(enum.IntEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


RESOLUTION_CODE = {
    CameraResolution.NATIVE:    2,
    CameraResolution.QQQQVGA:   8,
    CameraResolution.QQQVGA:    7,
    CameraResolution.QQVGA:     0,
    CameraResolution.QVGA:      1,
    CameraResolution.VGA:       2,
    CameraResolution.VGA4:      3,
}

COLOR_SPACE = {
    'kYuv': 0, 'kyUv': 1, 'kyuV': 2,
    'Rgb':  3, 'rGb':  4, 'rgB': 5,
    'Hsy':  6, 'hSy':  7, 'hsY': 8,

    'YUV422': 9,  # (Native Color)

    'YUV': 10, 'RGB': 11, 'HSY': 12,
    'BGR': 13, 'YYCbCr': 14,
    'H2RGB': 15, 'HSMixed': 16,

    'Depth': 17,        # uint16    - corrected distance from image plan (mm)
    'XYZ': 19,          # 3float32  - voxel xyz
    'Distance': 21,     # uint16    - distance from camera (mm)
    'RawDepth': 23,     # uint16    - distance from image plan (mm)
}

SERVICE_VIDEO = "ALVideoDevice"
SERVICE_MOTION = "ALMotion"

# Only take non-blurry pictures
HEAD_DELTA_THRESHOLD = 0.1


class NAOqiCamera(object):
    def __init__(self, session, resolution, rate):
        # type: (qi.Session, CameraResolution, int) -> None
        """
        Initialize NAOqi Camera.

        More information on paramters can be found at:
        http://doc.aldebaran.com/2-1/naoqi/vision/alvideodevice.html

        Parameters
        ----------
        session: qi.Session
            NAOqi Application Session
        resolution: CameraResolution
            NAOqi Camera Resolution
        index: int
            Which NAOqi Camera to use
        """
        self._session = session

        self._color_space = COLOR_SPACE['YUV422']
        self._color_space_3D = COLOR_SPACE['Distance']

        self._resolution = resolution
        self._resolution_3D = resolution

        self._rate = rate

        self._service = None
        self._motion = None
        self._client = None

    def __enter__(self):
        self._service = self._session.service(SERVICE_VIDEO)
        self._motion = self._session.service(SERVICE_MOTION)

        # TODO Check hasDepthCamera
        self._client = self._service.subscribeCameras(
            str(uuid.uuid4()),  # Random Client ID's to prevent name collision
            [int(NAOqiCameraIndex.TOP), int(NAOqiCameraIndex.DEPTH)],
            [RESOLUTION_CODE[self._resolution], RESOLUTION_CODE[self._resolution_3D]],
            [self._color_space, self._color_space_3D],
            self._rate
        )

        logger.info("NAOqiCamera started")

        return NAOqiImageSource(self._service,
                                self._client,
                                self._motion,
                                self._resolution,
                                self._rate,
                                self._color_space,
                                self._color_space_3D)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._service.unsubscribe(self._client)
        self._service = None
        self._motion = None
        self._client = None


class NAOqiImageSource(ImageSource):
    def __init__(self, service, client, motion, resolution, rate, color_space, color_space_3D):
        # type: (qi.Service, qi.Service, CameraResolution, int, int, int) -> None
        self._color_space = color_space
        self._color_space_3D = color_space_3D

        self._resolution = resolution
        self._resolution_3D = resolution

        self._rate = rate

        self._service = service
        self._client = client
        self._motion = motion

    @property
    def resolution(self):
        return self._resolution

    def capture(self):
        image_rgb, image_3D, view = None, None, None

        # TODO: Make sure these are the Head Yaw and Pitch at image capture time!?
        yaw, pitch = self._motion.getAngles("HeadYaw", False)[0], self._motion.getAngles("HeadPitch", False)[0]

        for image in self._service.getImagesRemote(self._client):
            # TODO: RGB and Depth Images are not perfectly synced, can they?
            width, height, _, _, _, _, data, camera, left, top, right, bottom = image

            if camera == NAOqiCameraIndex.DEPTH:
                # Convert from Millimeters to Meters
                # TODO: Make sure Image Bounds are actually the same for RGB and Depth Camera!
                image_3D = np.frombuffer(data, np.uint16).reshape(height, width).astype(np.float32) / 1000
            else:
                image_rgb = self._yuv2rgb(width, height, data)

                # Calculate Image Bounds in Radians
                # Apply Yaw and Pitch to Image Bounds
                # Bring Theta from [-PI/2,+PI/2] to [0, PI] Space
                phi_min, phi_max = right - yaw, left - yaw
                theta_min, theta_max = bottom + pitch + np.pi / 2, top + pitch + np.pi / 2
                view = Bounds(phi_min, theta_min, phi_max, theta_max)

        return Image(image_rgb, view, image_3D) if image_rgb is not None and view is not None else None

    def _yuv2rgb(self, width, height, data):
        # type: (int, int, bytes) -> np.ndarray
        """
        Convert from YUV422 to RGB Color Space

        Parameters
        ----------
        width: int
            Image Width
        height: int
            Image Height
        data: bytes
            Image Data

        Returns
        -------
        image_rgb: np.ndarray
        """

        X2 = width // 2

        YUV442 = np.frombuffer(data, np.uint8).reshape(height, X2, 4)

        RGB = np.empty((height, X2, 2, 3), np.float32)
        RGB[:, :, 0, :] = YUV442[..., 0].reshape(height, X2, 1)
        RGB[:, :, 1, :] = YUV442[..., 2].reshape(height, X2, 1)

        Cr = (YUV442[..., 1].astype(np.float32) - 128.0).reshape(height, X2, 1)
        Cb = (YUV442[..., 3].astype(np.float32) - 128.0).reshape(height, X2, 1)

        RGB[..., 0] += np.float32(1.402) * Cb
        RGB[..., 1] += - np.float32(0.71414) * Cb - np.float32(0.34414) * Cr
        RGB[..., 2] += np.float32(1.772) * Cr

        return RGB.clip(0, 255).astype(np.uint8).reshape(height, width, 3)
