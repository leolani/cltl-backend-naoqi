import unittest

import numpy as np
import soundfile as sf
from importlib_resources import path

from cltl.asr.wav2vec_asr import Wav2Vec2ASR


class TestWav2Vec2ASR(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.asr = Wav2Vec2ASR("facebook/wav2vec2-base-960h", 16000)

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.asr

    def test_resampling_stereo_to_mono(self):
        resampled = self.asr._resample(np.stack((np.ones((16,)), np.zeros((16,))), axis=1), 16000)
        self.assertEqual(resampled.shape, (16,))
        self.assertTrue(all(resampled == 0.5))

    def test_resampling_single_channel_is_squeezed(self):
        resampled = self.asr._resample(np.ones((16, 1)), 16000)
        self.assertEqual(resampled.shape, (16,))

    def test_resampling_single_channel(self):
        resampled = self.asr._resample(np.ones((16,)), 16000)
        self.assertEqual(resampled.shape, (16,))

    def test_speech_to_text(self):
        with path("resources", "test.wav") as wav:
            speech_array, sampling_rate = sf.read(wav)

        transcript = self.asr.speech_to_text(speech_array, sampling_rate)
        self.assertEqual("IT'S HEALTHIER TO COOK WITHOUT SUGAR", transcript.upper())