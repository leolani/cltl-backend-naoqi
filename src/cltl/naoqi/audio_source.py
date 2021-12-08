import enum
import logging
import uuid

import numpy as np
from Queue import Queue, Full, Empty
from cltl.naoqi.spi.audio import AudioSource

logger = logging.getLogger(__name__)


def reframe(queue, frame_size, frame_duration):
    buffer = []
    buffered = 0

    while True:
        try:
            chunk = queue.get(timeout=frame_duration)
        except Empty:
            continue

        buffer.append(chunk)
        buffered += chunk.shape[0]

        if buffered >= frame_size:
            np_buffer = np.concatenate(buffer)
            frames = [np_buffer[i:i + frame_size]
                      for i in range(0, np_buffer.shape[0], frame_size)]

            if frames[-1].shape[0] != frame_size:
                buffer = frames[-1:]
                buffered = buffer[0].shape[0]
                frames = frames[:-1]
            else:
                buffer = []
                buffered = 0

            for frame in frames:
                yield frame


class NAOqiMicrophoneIndex(enum.IntEnum):
    ALL = 0
    LEFT = 1
    RIGHT = 2
    FRONT = 3
    REAR = 4


class NAOqiMicrophone(object):
    SERVICE = "ALAudioDevice"

    def __init__(self, session, rate, channels, frame_size, index, buffer=4):
        """
        Initialize NAOqi Microphone.

        Information on parameters can be found at:
        http://doc.aldebaran.com/2-1/naoqi/audio/alaudiodevice.html

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        rate: int
            Microphone rate
        index: NAOqiMicrophoneIndex or int
            Which Microphone to Use
        """
        self.id = str(uuid.uuid4())[:6]

        self._index = index
        self._rate = rate
        self._channels = channels
        self._frame_size = frame_size
        self._buffer_size = buffer

        self._session = session
        self._service = None

    def __enter__(self):
        audio_source = NAOqiAudioSource(self._rate, self._channels, self._frame_size, self._index, self._buffer_size)

        self._service = self._session.service(NAOqiMicrophone.SERVICE)
        self._session.registerService(NAOqiAudioSource.__name__, audio_source)
        self._service.setClientPreferences(NAOqiAudioSource.__name__, self._rate, int(self._index), 0)
        self._service.subscribe(NAOqiAudioSource.__name__)

        logger.debug("Started NAOqiMicrophone")

        return audio_source

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._service.unsubscribe(NAOqiAudioSource.__name__)
        self._service = None

    @property
    def rate(self):
        return self._rate

    @property
    def channels(self):
        return self._channels

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def depth(self):
        return 2


class NAOqiAudioSource(AudioSource):
    def __init__(self, rate, channels, frame_size, index, buffer=4):
        """
        Initialize NAOqi Microphone.

        Information on parameters can be found at:
        http://doc.aldebaran.com/2-1/naoqi/audio/alaudiodevice.html

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        rate: int
            Microphone rate
        index: NAOqiMicrophoneIndex or int
            Which Microphone to Use
        """
        self.id = str(uuid.uuid4())[:6]

        self._index = index
        self._rate = rate
        self._channels = channels
        self._frame_size = frame_size

        self._active = False
        self._start_time = None
        self._time = None

        self._audio_queue = Queue(buffer)
        self._audio_generator = None
        self._buffer_size = buffer

    def __enter__(self):
        return self.start()

    def start(self):
        if self._audio_generator is not None:
            raise ValueError("Audio already open")

        # Empty the buffer to reduce latency
        for _ in range(self._buffer_size):
            try:
                self._audio_queue.get_nowait()
            except Empty:
                pass

        self._audio_generator = reframe(self._audio_queue, self._frame_size, self._frame_size/self.rate)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        self._audio_generator.close()
        self._audio_generator = None

    def __iter__(self):
        return iter(self.audio)

    def next(self):
        return next(self.audio)

    @property
    def audio(self):
        return self._audio_generator

    @property
    def rate(self):
        return self._rate

    @property
    def channels(self):
        return self._channels

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def depth(self):
        return 2

    @property
    def active(self):
        return self._active

    # TODO
    # @property
    # def time(self):
    #     return self._mic_time - self._start_time

    def processRemote(self, channels, samples, timestamp, buffer):
        # type: (int, int, Tuple[int, int], bytes) -> None
        """
        Process Audio Window from Pepper/Nao

        This function must be exactly called "processRemote", according to NAOqi specifications.

        Make sure this thread is idle to receive calls from NAOqi to 'processRemote', otherwise frames will be dropped!

        Parameters
        ----------
        channels: int
            Number of Channels
        samples: int
            Number of Samples
        timestamp: (int, int)
            seconds, millis since boot
        buffer: bytes
            Audio Buffer
        """
        audio = np.frombuffer(buffer, np.int16)
        if channels != 1:
            audio.reshape(-1, channels)

        if channels == 4 and self.channels == 1:
            audio = audio.mean(axis=1)
        elif channels != self.channels:
            raise ValueError("Received " + str(channels) + " channels, expected " + str(self.channels))

        try:
            self._audio_queue.put_nowait(audio)
        except Full as e:
            logger.debug("Dropped frame: %s", audio.shape)
            pass
