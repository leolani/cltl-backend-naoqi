from __future__ import unicode_literals

import logging

from cltl.naoqi.spi.text import TextOutput

logger = logging.getLogger(__name__)


class NAOqiTextToSpeech(TextOutput):
    """
    NAOqi Text to Speech

    Parameters
    ----------
    session: qi.Session
        Qi Application Session.
    speed: int
        The speed of speech.
    """
    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, speed):
        # Subscribe to NAOqi Text to Speech Service
        self._speed = speed
        self._service = session.service(NAOqiTextToSpeech.SERVICE)
        logger.debug("Booted")

    def consume(self, text, language=None, animation=None):
        """
        Say something through Text to Speech.

        Parameters
        ----------
        text: str
        language: str
        animation: str
        """
        text = text.replace('...', r'\\pau=1000\\')

        if animation:
            self._service.say(r"\\rspd={2}\\^startTag({1}){0}^stopTag({1})".format(text, animation, self._speed))
        else:
            self._service.say(r"\\rspd={1}\\{0}".format(text, self._speed))
