import collections
import enum
import logging

import numpy as np

logger = logging.getLogger(__name__)


class CameraResolution(enum.Enum):
    """
    Image height and width.
    """
    NATIVE = -1, -1
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280

    @property
    def height(self):
        return self.value[0]

    @property
    def width(self):
        return self.value[1]


Bounds = collections.namedtuple('Bounds', ['x0', 'x1', 'y0', 'y1'])


class Image(object):
    """
    Abstract Image Container

    Parameters
    ----------
    image: np.ndarray
        RGB Image (height, width, 3) as Numpy Array
    view: Bounds
        View Bounds (View Space) in Spherical Coordinates (Phi, Theta)
    depth: np.ndarray
        Image Depth (height, width) as Numpy Array
    """
    def __init__(self, image, view, depth):
        self.image = image
        self.view = view
        self.depth = depth

    @property
    def resolution(self):
        try:
            return CameraResolution(self.image.shape[:2])
        except ValueError:
            return CameraResolution.NATIVE
