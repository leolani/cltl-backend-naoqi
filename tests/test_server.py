import base64
import json
import unittest

import numpy as np
from Queue import Queue

from cltl.naoqi.api.camera import CameraResolution, Image, Bounds
from cltl.naoqi.server import BackendServer
from cltl.naoqi.spi.audio import AudioSource
from cltl.naoqi.spi.image import ImageSource
from cltl.naoqi.spi.text import TextOutput

AUDIO_ARRAY = [np.ones((10,), dtype=np.int16)] * 10


#TODO centralize
def _deserialize_numpy(image_json):
    if not image_json:
        return None

    data_string = image_json["data"]
    shape = image_json["shape"]
    dtype = image_json["dtype"]

    return np.frombuffer(base64.b64decode(data_string), dtype=dtype).reshape(shape)


class TestMic(AudioSource):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def start(self):
        return self

    def stop(self):
        pass

    @property
    def audio(self):
        return iter(AUDIO_ARRAY)

    @property
    def rate(self):
        return 1

    @property
    def channels(self):
        return 1

    @property
    def frame_size(self):
        return 10

    @property
    def depth(self):
        return 2


class TestCam(ImageSource):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def resolution(self):
        return CameraResolution.QQQQVGA

    def capture(self):
        return Image(np.ones(self.resolution.value), Bounds(*((0.0, 0.0) + self.resolution.value)), np.zeros(self.resolution.value))


class TestTTS(TextOutput):
    def __init__(self):
        self.consumed = Queue()

    def consume(self, text, language=None):
        self.consumed.put(text)




class BackendServerTest(unittest.TestCase):
    def test_audio(self):
        mic = TestMic()
        camera = TestCam()
        tts = TestTTS()
        server = BackendServer(mic, camera, tts)
        server._start_for_testing()

        with server.app.test_client() as client:
            audio_response = client.get("/audio")
            self.assertEqual(200, audio_response.status_code)
        audio = [frame for frame in audio_response.iter_encoded()]

        np.testing.assert_array_equal(AUDIO_ARRAY, [np.frombuffer(frame, dtype=np.int16) for frame in audio])

    def test_video(self):
        mic = TestMic()
        camera = TestCam()
        tts = TestTTS()
        server = BackendServer(mic, camera, tts)
        server._start_for_testing()

        with server.app.test_client() as client:
            image_response = client.get("/image")
            self.assertEqual(200, image_response.status_code)
        image_json = json.loads(image_response.data)

        image = _deserialize_numpy(image_json['image'])
        depth = _deserialize_numpy(image_json['depth'])
        np.testing.assert_array_equal(np.ones(camera.resolution.value), image)
        np.testing.assert_array_equal(Bounds(*((0.0, 0.0) + camera.resolution.value)), image_json['view'])
        np.testing.assert_array_equal(np.zeros(camera.resolution.value), depth)

    def test_tts(self):
        mic = TestMic()
        camera = TestCam()
        tts = TestTTS()
        server = BackendServer(mic, camera, tts)
        server._start_for_testing()

        with server.app.test_client() as client:
            response = client.post("/text", data="This is a test text")
            self.assertEqual(200, response.status_code)

        self.assertEqual("This is a test text", tts.consumed.get(timeout=1))