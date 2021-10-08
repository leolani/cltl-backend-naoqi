from dataclasses import dataclass

from cltl_service.backend.schema import TextSignalEvent
from emissor.representation.container import Index
from emissor.representation.scenario import Modality


@dataclass
class AsrTextSignalEvent(TextSignalEvent):
    confidence: float
    audio_segment: Index

    @classmethod
    def create(cls, signal_id: str, timestamp: float, transcript: str, confidence: float, audio_segment: Index):
        return cls(cls.__name__, signal_id, timestamp, Modality.TEXT, [], transcript, confidence, audio_segment)