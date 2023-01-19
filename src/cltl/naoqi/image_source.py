import enum
import logging
import uuid

import numpy as np
import qi
import vision_definitions

from cltl.naoqi.api.camera import Image, Bounds, CameraResolution
from cltl.naoqi.spi.image import ImageSource

logger = logging.getLogger(__name__)


class NAOqiCameraIndex(enum.IntEnum):
    """
    See also:
    http://doc.aldebaran.com/2-5/naoqi/vision/alvideodevice.html?highlight=alvideodevice
    """
    TOP = vision_definitions.kTopCamera
    BOTTOM = vision_definitions.kBottomCamera
    DEPTH = vision_definitions.kDepthCamera


RESOLUTION_CODE = {
    CameraResolution.NATIVE:    vision_definitions.kVGA,
    CameraResolution.QQQQVGA:   vision_definitions.kQQQQVGA,
    CameraResolution.QQQVGA:    vision_definitions.kQQQVGA,
    CameraResolution.QQVGA:     vision_definitions.kQQVGA,
    CameraResolution.QVGA:      vision_definitions.kQVGA,
    CameraResolution.VGA:       vision_definitions.kVGA,
    CameraResolution.VGA4:      vision_definitions.k4VGA
}

class ColorSpace(enum.IntEnum):
    RGB = vision_definitions.kRGBColorSpace
    DEPTH = vision_definitions.kDepthColorSpace


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

        self._resolution = resolution
        self._resolution_3D = resolution

        self._rate = rate

        self._service = None
        self._motion = None
        self._client = None

    def __enter__(self):
        self._service = self._session.service(SERVICE_VIDEO)
        self._motion = self._session.service(SERVICE_MOTION)

        camera_indexes = [int(NAOqiCameraIndex.TOP)]
        resolutions = [RESOLUTION_CODE[self._resolution]]
        color_spaces = [ColorSpace.RGB.value]

        if self._service.hasDepthCamera():
            camera_indexes += [int(NAOqiCameraIndex.DEPTH)]
            resolutions += [RESOLUTION_CODE[self._resolution_3D]]
            color_spaces += [ColorSpace.DEPTH.value]

        self._client = self._service.subscribeCameras(
            str(uuid.uuid4()),
            camera_indexes,
            resolutions,
            color_spaces,
            self._rate
        )

        logger.info("NAOqiCamera started")

        return NAOqiImageSource(self._service,
                                self._client,
                                self._motion,
                                self._resolution,
                                self._rate,
                                bool(len(camera_indexes) > 1))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._service.unsubscribe(self._client)
        self._service = None
        self._motion = None
        self._client = None


class NAOqiImageSource(ImageSource):
    def __init__(self, service, client, motion, resolution, rate, multistream):
        self._resolution = resolution

        self._rate = rate
        self._multistream = multistream

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

        if self._multistream:
            images = self._service.getImagesRemote(self._client)
        else:
            images = [self._service.getImageRemote(self._client)]

        for image in images:
            # TODO: RGB and Depth Images are not perfectly synced, can they?
            width, height, _, _, _, _, data, camera, left, top, right, bottom = image

            if camera == NAOqiCameraIndex.DEPTH:
                # Convert from Millimeters to Meters
                # TODO: Make sure Image Bounds are actually the same for RGB and Depth Camera!
                image_3D = np.frombuffer(data, np.uint16).reshape(height, width).astype(np.float32) / 1000
            else:
                image_rgb =  np.frombuffer(data, np.uint8).reshape(height, width, 3)

                # TODO replace by helper method from Qi Framework
                # Calculate Image Bounds in Radians
                # Apply Yaw and Pitch to Image Bounds
                # Bring Theta from [-PI/2,+PI/2] to [0, PI] Space
                phi_min, phi_max = right - yaw, left - yaw
                theta_min, theta_max = bottom + pitch + np.pi / 2, top + pitch + np.pi / 2
                view = Bounds(phi_min, theta_min, phi_max, theta_max)

        return Image(image_rgb, view, image_3D) if image_rgb is not None and view is not None else None