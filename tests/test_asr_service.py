import threading
import unittest
from queue import Queue, Empty
from typing import Iterable

import numpy as np
from cltl.backend.spi.audio import AudioSource
from cltl.combot.infra.event import Event
from cltl.combot.infra.event.memory import SynchronousEventBus
from cltl_service.vad.schema import VadAnnotation, VadMentionEvent
from emissor.representation.container import Index

from cltl.asr.api import ASR
from cltl_service.asr.service import AsrService


def wait(lock: threading.Event):
    if not lock.wait(1):
        raise unittest.TestCase.failureException("Latch timed out")


frame = np.random.random((16, 1)).astype(np.int16)

def test_source(start, audio_started, audio_ended):
    class TestSource(AudioSource):
        def __init__(self, url, offset, length):
            self.offset = offset

        @property
        def audio(self) -> Iterable[np.array]:
            wait(start)
            yield from [frame, frame]
            audio_started.set()
            yield from [frame, frame]
            audio_ended.set()

        @property
        def rate(self):
            return 16000

        @property
        def channels(self):
            return 1

        @property
        def frame_size(self):
            return 16

        @property
        def depth(self):
            return 2

    return TestSource


class DummyASR(ASR):
    def speech_to_text(self, audio: np.array, sampling_rate: int) -> str:
        return "test transcript" if len(audio) == 4 * 16 and np.array_equal(audio[:16], frame) else None


class TestASR(unittest.TestCase):
    def setUp(self) -> None:
        self.event_bus = SynchronousEventBus()
        self.asr_service = None

    def tearDown(self) -> None:
        if self.asr_service:
            self.asr_service.stop()

    def test_events_from_asr_service(self):
        start = threading.Event()
        audio_started = threading.Event()
        audio_ended = threading.Event()

        self.asr_service = AsrService("vad_topic", "asr_topic", DummyASR(),
                                      test_source(start, audio_started, audio_ended), self.event_bus, None)
        self.asr_service.start()

        segment = Index.from_range("signal_id", 0, 10)
        annotation = VadAnnotation.for_activation(1.0, "test_source")
        payload =  VadMentionEvent.create(segment, annotation)
        self.event_bus.publish("vad_topic", Event.for_payload(payload))

        events = Queue()

        def receive_event(event):
            events.put(event)

        self.event_bus.subscribe("asr_topic", receive_event)

        start.set()
        wait(audio_ended)

        event = events.get(block=True, timeout=0.1)
        self.assertEqual("test transcript", event.payload.text)
        self.assertEqual("signal_id", event.payload.audio_segment[0].container_id)

