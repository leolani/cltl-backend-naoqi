from collections import defaultdict
from queue import Empty, Queue, Full
from threading import Lock
from typing import Iterable

from cltl.chatui.api import ResponseCache, Utterance


class MemoryResponseCache(ResponseCache):
    def __init__(self):
        self._chats = dict()
        self._lock = Lock()

    def append(self, utterance: Utterance) -> None:
        try:
            self._chats[utterance.chat_id].put(utterance)
        except KeyError:
            with self._lock:
                if not utterance.chat_id in self._chats:
                    self._chats[utterance.chat_id] = Queue()
            self.append(utterance)

    def get_utterances(self, chat_id: str) -> Iterable[Utterance]:
        if not chat_id in self._chats:
            raise ValueError("No chat with id " + chat_id)

        chat = self._chats[chat_id]
        responses = []
        while True:
            try:
                responses.append(chat.get_nowait())
            except Empty:
                break

        return responses