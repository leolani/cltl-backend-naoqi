import abc
from dataclasses import dataclass
from typing import Optional, Iterable


@dataclass
class Utterance:
    chat_id: str
    speaker: str
    text: str


class ResponseCache(abc.ABC):
    def append(self, utterances: Iterable[Utterance]):
        raise NotImplementedError("")

    def get_utterances(self, chat_id: str):
        raise NotImplementedError("")