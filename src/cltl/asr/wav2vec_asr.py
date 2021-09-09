import os

import time

import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

from cltl.asr.api import ASR
from cltl.asr.util import store_wav


class Wav2Vec2ASR(ASR):
    def __init__(self, model_id: str, sampling_rate: int, storage: str = None):
        self.processor = Wav2Vec2Processor.from_pretrained(model_id)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_id)

        self.sampling_rate = sampling_rate

        self._storage = storage

    def speech_to_text(self, audio: np.array, sampling_rate: int) -> str:
        if not sampling_rate:
            sampling_rate = self.sampling_rate

        raw_audio = self._resample(audio, sampling_rate)
        if self._storage:
            store_wav(raw_audio, sampling_rate, str(os.path.join(self._storage, f"asr-{time.time()}.wav")))

        representation = self.processor(raw_audio, sampling_rate=self.sampling_rate, return_tensors="pt").input_values
        token_logits = self.model(representation).logits
        predicted_tokens = np.argmax(token_logits.detach().numpy(), axis=2)

        return self.processor.decode(predicted_tokens[0])

    def _resample(self, audio, sampling_rate):
        if not audio.dtype == np.int16:
            raise ValueError(f"Invalid sample depth {audio.dtype}, expected np.int16")

        if sampling_rate != self.sampling_rate:
            raise ValueError(f"Unsupported sampling rate: {sampling_rate}, expected {self.sampling_rate}")

        if audio.ndim == 1 or audio.shape[1] == 1:
            return audio.squeeze()

        if audio.ndim > 2 or audio.shape[1] > 2:
            raise ValueError(f"audio must have at most two channels, shape was {audio.shape}")

        return audio.mean(axis=1, dtype=np.int16).ravel()
