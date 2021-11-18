import argparse
import enum
import logging
import os

import qi

from cltl.host.server import BackendServer
from cltl.naoqi.api.camera import CameraResolution
from cltl.naoqi.audio_source import NAOqiMicrophoneIndex

logger = logging.getLogger(__name__)


class Env(enum.Enum):
    CLTL_MIC_IDX = 0
    CLTL_MIC_BUFFER = 3
    CLTL_MIC_FRAME_DURATION = 4
    CLTL_CAM_RATE = 5
    CLTL_CAM_RES = 6
    CLTL_LANG = 8
    CLTL_NAOQI_IP = 9
    CLTL_NAOQI_PORT = 10
    CLTL_PORT = 11
    CLTL_LOG_LEVEL = 12


def env_or_default(env_var, default):
    var = env_var.name

    return os.environ[var] if var in os.environ and os.environ[var] else default


def main():
    logging.basicConfig(
        level=env_or_default(Env.CLTL_LOG_LEVEL, logging.DEBUG),
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description='Backend application to serve sensor data from a host machine')
    parser.add_argument('--frame_duration', type=int, choices=[10, 20, 30],
                        default=env_or_default(Env.CLTL_MIC_FRAME_DURATION, 30),
                        help="Duration of audio frames in milliseconds. Alternatively set " + Env.CLTL_MIC_FRAME_DURATION.name)
    parser.add_argument('--mic_index', type=int, choices=[idx.value for idx in NAOqiMicrophoneIndex],
                        default=env_or_default(Env.CLTL_MIC_IDX, 2),
                        help="Microphone index, 0 implies 4 channels 48kHz, all others 1 channel 16kHz. Alternatively set " + Env.CLTL_MIC_IDX.name)
    parser.add_argument('--mic_buffer', type=int, choices=[1, 2, 4, 8, 16, 32, 64, 128, 256],
                        default=env_or_default(Env.CLTL_MIC_BUFFER, 2),
                        help="Microphone buffer, corresponds to 170ms per element, Alternatively set " + Env.CLTL_MIC_BUFFER.name)
    parser.add_argument('--resolution', type=str, choices=[res.name for res in CameraResolution],
                        default=env_or_default(Env.CLTL_CAM_RES, CameraResolution.QVGA.name),
                        help="Camera resolution to use. Alternatively set " + Env.CLTL_CAM_RES.name)
    # Unused
    # parser.add_argument('--cam_index', type=int,
    #                     default=env_or_default(Env.CLTL_CAM_IDX, 0), choices=[idx.value for idx in NAOqiCameraIndex],
    #                     help="Camera index of the camera to use. Alternatively set " + Env.CLTL_CAM_IDX.name)
    parser.add_argument('--cam_rate', type=int,
                        default=env_or_default(Env.CLTL_CAM_RATE, 2),
                        help="Camera rate to use, < 30fps, recommended for QVGA: < 11, VGA < 2.5. Alternatively set " + Env.CLTL_CAM_RATE.name)
    parser.add_argument('--naoqi_ip', type=str, required=True,
                        help="IP of the robot. Alternatively set " + Env.CLTL_NAOQI_IP.name)
    parser.add_argument('--naoqi_port', type=int,
                        default=env_or_default(Env.CLTL_NAOQI_PORT, 9559),
                        help="NAOqi port of the robot. Alternatively set " + Env.CLTL_NAOQI_PORT.name)
    parser.add_argument('--port', type=int,
                        default=env_or_default(Env.CLTL_PORT, 8000),
                        help="Web server port. Alternatively set " + Env.CLTL_PORT.name)
    args, _ = parser.parse_known_args()

    logger.info("Starting webserver with args: %s", args)

    naoqi_url = "tcp://{}:{}".format(args.naoqi_ip, args.naoqi_port)
    naoqi_app = qi.Application(["NAOqi Backend", "--qi-url=" + naoqi_url ])
    try:
        naoqi_app.start()
    except RuntimeError as e:
        raise RuntimeError("Couldn't connect to robot @ {}:{}\n\tOriginal Error: {}"
                           .format(args.naoqi_ip, args.naoqi_port, e))

    rate = 48000 if args.mic_index == 0 else 16000
    channels = 1
    server = BackendServer(naoqi_app.session, rate, channels, args.frame_duration * rate // 1000,
                           args.mic_index, args.mic_buffer,
                           CameraResolution[args.resolution.upper()], args.cam_rate)
    server.run(host="0.0.0.0", port=args.port)


if __name__ == '__main__':
    main()