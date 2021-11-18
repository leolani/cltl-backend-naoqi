import collections
import logging

logger = logging.getLogger(__name__)


AUDIO_RESOURCE_NAME = "cltl.backend.api.audio"
"""Resource name to be shared with the speaker to mute the microphone when the speaker is active.
The AbstractMicrophone holds a reader-lock on this resource.
"""
MIC_RESOURCE_NAME = "cltl.backend.api.microphone"
"""Resource name to be shared with application components that allows to retract microphone access from those components.
The AbstractMicrophone holds a writer-lock on this resource.
"""


AudioParameters = collections.namedtuple('AudioParameters', ['sampling_rate', 'channels', 'frame_size', 'sample_width'])


class AudioFormat:
    L16_MONO_16K_30MS = AudioParameters(16000, 1, 480, 2)