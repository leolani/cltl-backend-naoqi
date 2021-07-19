import abc
from dataclasses import dataclass
from typing import Optional, Iterable


@dataclass
class Utterance:
    chat_id: str
    speaker: str
    text: str


class Chat(abc.ABC):
    def get_utterances(self, chat_id: str, start: int = None, end: int = None) -> Iterable[str]:
        raise NotImplementedError("")

    def get_utterance(self, chat_id: str, seq: int) -> Utterance:
        raise NotImplementedError("")

    def append(self, utterance: Utterance) -> None:
        raise NotImplementedError("")