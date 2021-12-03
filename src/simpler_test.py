import time
import uuid

import numpy as np
import qi


class AudioTestModule(object):
    def processRemote(self, channels, samples, timestamp, buffer):
        # type: (int, int, Tuple[int, int], bytes) -> None
        audio = np.frombuffer(buffer, np.int16)
        try:
            if channels != 1:
                audio.reshape(-1, channels)
        except Exception as e:
            print("Error in processRemote:", e)

        print("Received buffer:", audio.shape, channels, samples)


SERVICE_VIDEO = "ALVideoDevice"
SERVICE_MOTION = "ALMotion"
COLOR_SPACE = {
    'YUV422': 9,  # (Native Color)
    'Distance': 21,     # uint16    - distance from camera (mm)
}


class ImageTest(object):
    def __init__(self, session):
        self._session = session
        self._service = self._session.service(SERVICE_VIDEO)
        self._motion = self._session.service(SERVICE_MOTION)

    def start(self):
        self._client = self._service.subscribeCameras(
            str(uuid.uuid4()),  # Random Client ID's to prevent name collision
            [0, 2],
            [0, 0],
            [COLOR_SPACE['YUV422'], COLOR_SPACE['Distance']],
            1)

        return self

    def stop(self):
        self._service.unsubscribe(self._client)

    def capture(self):
        yaw, pitch = self._motion.getAngles("HeadYaw", False)[0], self._motion.getAngles("HeadPitch", False)[0]
        print("Received motion info:", yaw, pitch)

        for image in self._service.getImagesRemote(self._client):
            # TODO: RGB and Depth Images are not perfectly synced, can they?
            width, height, _, _, _, _, data, camera, left, top, right, bottom = image

            print("Received image:", np.frombuffer(data, np.uint16).shape, width, height, camera)


if __name__ == '__main__':
    naoqi_url = "tcp://{}:{}".format("192.168.1.176", 9559)
    naoqi_app = qi.Application(["NAOqi Backend", "--qi-url=" + naoqi_url])

    try:
        naoqi_app.start()
    except RuntimeError as e:
        print("Couldn't connect to robot @ {}:{}\n\tOriginal Error: {}".format("192.168.1.176", 9559, e))

    try:
        audio_service_name = "TestAudioService"
        test_audio_service = AudioTestModule()

        service = naoqi_app.session.service("ALAudioDevice")
        naoqi_app.session.registerService(audio_service_name, test_audio_service)

        service.setClientPreferences(audio_service_name, 16000, 3, 0)
        service.subscribe(audio_service_name)

        time.sleep(10)

        service.unsubscribe(audio_service_name)
    except Exception as e:
        print("Error running audio test:", e)

    try:
        image_source = ImageTest(naoqi_app.session)
        image_source.start()
        image_source.capture()
        image_source.stop()
    except Exception as e:
        print("Error running image test:", e)