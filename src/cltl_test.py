import qi

from cltl.naoqi.api.camera import CameraResolution
from cltl.naoqi.audio_source import NAOqiMicrophone
from cltl.naoqi.image_source import NAOqiCamera

if __name__ == '__main__':
    naoqi_url = "tcp://{}:{}".format("192.168.1.176", 9559)
    naoqi_app = qi.Application(["NAOqi Backend", "--qi-url=" + naoqi_url])

    try:
        naoqi_app.start()
    except RuntimeError as e:
        print("Couldn't connect to robot @ {}:{}\n\tOriginal Error: {}".format("192.168.1.176", 9559, e))

    mic = NAOqiMicrophone(naoqi_app.session, 16000, 1, 480, 3)
    with mic as audio_source:
        with audio_source as source:
            for _ in range(10):
                print("Received frame:", next(source.audio).shape)

    camera = NAOqiCamera(naoqi_app.session, CameraResolution.QVGA, 1)
    with camera as image_source:
        image = image_source.capture()
        print("Captured image:", image.image.shape)