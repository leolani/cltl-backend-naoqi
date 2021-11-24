"""Example: Get Signal from Front Microphone & Calculate its rms Power"""

import argparse
import time

import qi


class SoundProcessingModule(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__(self):
        """
        Initialise services and variables.
        """
        super(SoundProcessingModule, self).__init__()

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Compute RMS from mic.
        """
        print("Received buffer of length " + str(len(inputBuffer)))


def test_app():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default="app",
                        help="test function")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--pcip", type=str, default="0.0.0.0",
                        help="PC IP address. ")
    parser.add_argument("--pcport", type=int, default=37267,
                        help="PC port number")

    args = parser.parse_args()

    module_name = "SoundProcessingModule"

    try:
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application([module_name,
                              "--qi-url=" + connection_url,
                              "--qi-listen-url=tcp://" + args.pcip + ":" + str(args.pcport)])
    except RuntimeError as e:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                                                                                             "Please check your script arguments. Run with -h option for help. " + str(
            e))
        raise e

    MySoundProcessingModule = SoundProcessingModule()

    try:
        app.start()
        session = app.session
        audio_service = session.service("ALAudioDevice")
        app.session.registerService(module_name, MySoundProcessingModule)
    except Exception as e:
        print("Failed to start: ", str(e))
        raise e

    audio_service.setClientPreferences(module_name, 16000, 3, 0)
    audio_service.subscribe(module_name)

    # Get the service ALAudioDevice.

    app.session.registerService(module_name, MySoundProcessingModule)

    time.sleep(15)

    audio_service.unsubscribe(module_name)


def test_session():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default="app",
                        help="test function")
    parser.add_argument("--pcip", type=str, default="0.0.0.0",
                        help="PC IP address. ")
    parser.add_argument("--pcport", type=int, default=37267,
                        help="PC port number")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()

    module_name = "SoundProcessingModule"

    try:
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application([module_name, "--qi-url=" + connection_url])
    except RuntimeError as e:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                                                                                             "Please check your script arguments. Run with -h option for help. " + str(
            e))
        raise e

    MySoundProcessingModule = SoundProcessingModule()

    try:
        app.start()
        session = app.session
        session.listen("tcp://" + args.pcip + ":" + str(args.pcport))
        audio_service = session.service("ALAudioDevice")
        app.session.registerService(module_name, MySoundProcessingModule)
    except Exception as e:
        print("Failed to start: ", str(e))
        raise e

    audio_service.setClientPreferences(module_name, 16000, 3, 0)
    audio_service.subscribe(module_name)

    # Get the service ALAudioDevice.

    app.session.registerService(module_name, MySoundProcessingModule)

    time.sleep(15)

    audio_service.unsubscribe(module_name)


def run_test(fct):
    print("\n\n\n=========== " + fct.__name__ + " ============\n\n")
    try:
        fct()
    except Exception as e:
        print(str(e))

    print("================================================")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default="app",
                        help="test function")
    parser.add_argument("--pcip", type=str, default="0.0.0.0",
                        help="PC IP address. ")
    parser.add_argument("--pcport", type=int, default=37267,
                        help="PC port number")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()

    if args.test == "app":
        run_test(test_app)
    elif args.test == "session":
        run_test(test_session)
