import argparse
import logging
import os

import enum
import qi

logger = logging.getLogger(__name__)


class Env(enum.Enum):
    CLTL_NAOQI_IP = 6
    CLTL_NAOQI_PORT = 7
    CLTL_PORT = 8
    CLTL_LOG_LEVEL = 9
    CLTL_SERVER = 9


def env_or_default(env_var, default):
    var = env_var.name

    return os.environ[var] if var in os.environ and os.environ[var] else default


def main():
    logging.basicConfig(
        level=env_or_default(Env.CLTL_LOG_LEVEL, logging.WARNING),
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description='Backend application to serve sensor data from a host machine')
    parser.add_argument('--naoqi-ip', type=str, required=True,
                        help="IP of the robot. Alternatively set " + Env.CLTL_NAOQI_IP.name)
    parser.add_argument('--naoqi-port', type=int,
                        default=env_or_default(Env.CLTL_NAOQI_PORT, 9559),
                        help="NAOqi port of the robot. Alternatively set " + Env.CLTL_NAOQI_PORT.name)
    parser.add_argument('--server', type=str,
                        help="server ip")
    args, _ = parser.parse_known_args()

    logger.info("Starting webserver with args: %s", args)

    naoqi_url = "tcp://{}:{}".format(args.naoqi_ip, args.naoqi_port)
    naoqi_app = qi.Application(["NAOqi Backend", "--qi-url=" + naoqi_url ])
    try:
        naoqi_app.start()
    except RuntimeError as e:
        raise RuntimeError("Couldn't connect to robot @ {}:{}\n\tOriginal Error: {}"
                           .format(args.naoqi_ip, args.naoqi_port, e))


    service = naoqi_app.session.service("ALTabletService")
    service.setOnTouchWebviewScaleFactor(1)
    service.hide()

    service.showWebview("http://" + args.server)


if __name__ == '__main__':
    main()