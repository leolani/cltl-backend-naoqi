import abc

import numpy as np


class ASR(abc.ABC):
    def speech_to_text(self, audio: np.ndarray, sampling_rate: int) -> str:
        """
        Transcribe the provided audio sample to text.

        Parameters
        ----------
        audio : np.array
            The binary audio data containing speech.
            The provided np.array must be either of shape (n), (n, 1) for mono
            or (n, 2) for stereo input, where n is the number of samples
            contained in the audio.
        sampling_rate : int
            The sampling rate of the audio data. If supported by the
            implementation, a falsy value may be passed to use a default sample
            rate. It is not recommended for implementations to provide the
            sampling rate as default argument, as this can lead to hard to
            detect errors if sampling rates don't match.

        Returns
        -------
        str
            Text transcript of the audio input.
        """
        raise NotImplementedError()