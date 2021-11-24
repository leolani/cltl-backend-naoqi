#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Get Signal from Front Microphone & Calculate its rms Power"""

import argparse
import time

import naoqi


# Global variable to store the SoundProcessingModule module instance
SoundProcessing = None


class SoundProcessingModule(naoqi.ALModule):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__( self, name):
        """
        Initialise services and variables.
        """
        naoqi.ALModule.__init__(self, name)

    def process(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        print("Received buffer of length " + str(len(inputBuffer)) + " at " + str(timeStamp))

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Compute RMS from mic.
        """
        print("Received remote buffer of length " + str(len(inputBuffer)) + " at " + str(timeStamp))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--brokerport", type=int, default=9558,
                        help="Broker port number")

    args = parser.parse_args()

    # We need this broker to be able to construct
    # NAOnaoqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = naoqi.ALBroker("myBroker",
                        "0.0.0.0",  # listen to anyone
                        args.brokerport,  # find a free port and use it
                        args.ip,  # parent broker IP
                        args.port)  # parent broker port


    global SoundProcessing
    SoundProcessing = SoundProcessingModule("SoundProcessing")

    audio = naoqi.ALProxy("ALAudioDevice")
    audio.setClientPreferences("SoundProcessing", 16000, 3, 0)
    audio.subscribe("SoundProcessing")

    time.sleep(15)

    audio.unsubscribe("SoundProcessing")
    myBroker.shutdown()