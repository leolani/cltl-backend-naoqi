from collections import defaultdict
from typing import Iterable

from cltl.chatui.api import Chat, Utterance


class MemoryChat(Chat):
    def __init__(self):
        self._chats = defaultdict(list)

    def append(self, utterance: Utterance) -> None:
        chat = self._chats[utterance.chat_id]
        chat.append(utterance)

    def get_utterances(self, chat_id: str, start: int = None, end: int = None) -> Iterable[Utterance]:
        if not chat_id in self._chats:
            raise ValueError("No chat with id " + chat_id)

        chat = self._chats[chat_id]

        start_idx = start if start is not None else 0
        end_idx = end if end is not None else len(chat)

        return chat[start_idx:end_idx]

    def get_utterance(self, chat_id: str, seq: int) -> str:
        return self._chats[chat_id][seq]
