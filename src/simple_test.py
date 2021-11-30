#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Get Signal from Front Microphone & Calculate its rms Power"""

import argparse
import subprocess
import time

import qi


class SoundProcessingModule(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__( self):
        """
        Initialise services and variables.
        """
        super(SoundProcessingModule, self).__init__()


    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Compute RMS from mic.
        """
        print("Received buffer of length " + str(len(inputBuffer)))


def list_ports():
    bashCommand = "lsof -i"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("Ports:")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--pcport", type=int, default=9558,
                        help="Container port number")

    args = parser.parse_args()

    module_name = "SoundProcessingModule"

    try:
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application([module_name + "App", "--qi-url=" + connection_url])
    except RuntimeError as e:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help. " + str(e))
        raise e

    MySoundProcessingModule = SoundProcessingModule()

    app.start()
    session = app.session
    session.listen("tcp://0.0.0.0:" + str(args.pcport))

    list_ports()

    audio_service = session.service("ALAudioDevice")

    list_ports()

    app.session.registerService(module_name, MySoundProcessingModule)

    list_ports()

    audio_service.setClientPreferences(module_name, 16000, 3, 0)
    audio_service.subscribe(module_name)
    # Get the service ALAudioDevice.

    list_ports()

    time.sleep(15)

    audio_service.unsubscribe(module_name)