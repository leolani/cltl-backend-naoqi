import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

from cltl.asr.api import ASR


class Wav2Vec2ASR(ASR):
    def __init__(self, model_id, sampling_rate):
        self.processor = Wav2Vec2Processor.from_pretrained(model_id)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_id)

        self.sampling_rate = sampling_rate

    def speech_to_text(self, audio: np.array, sampling_rate: int) -> str:
        if not sampling_rate:
            sampling_rate = self.sampling_rate

        raw_audio = self._resample(audio, sampling_rate)

        representation = self.processor(raw_audio, sampling_rate=self.sampling_rate, return_tensors="pt").input_values
        token_logits = self.model(representation).logits
        predicted_tokens = np.argmax(token_logits.detach().numpy(), axis=2)

        return self.processor.decode(predicted_tokens[0])

    def _resample(self, audio, sampling_rate):
        if sampling_rate != self.sampling_rate:
            raise ValueError(f"Unsupported sampling rate: {sampling_rate}, expected {self.sampling_rate}")

        if audio.ndim == 1 or audio.shape[1] == 1:
            return audio.squeeze()

        if audio.ndim > 2 or audio.shape[1] > 2:
            raise ValueError(f"audio must have at most two channels, shape was {audio.shape}")

        return np.mean(audio, axis=1).squeeze()


if __name__ == '__main__':
    # Try code from
    # https://colab.research.google.com/drive/1FjTsqbYKphl9kL-eILgUc-bl4zVThL8F?usp=sharing#scrollTo=al9Luo4LPpwJ

    from datasets import load_dataset

    timit = load_dataset("timit_asr")
    print(timit)

    import random
    import pandas as pd

    def show_random_elements(dataset, num_examples=1):
        assert num_examples <= len(dataset), "Can't pick more elements than there are in the dataset."
        picks = []
        for _ in range(num_examples):
            pick = random.randint(0, len(dataset) - 1)
            while pick in picks:
                pick = random.randint(0, len(dataset) - 1)
            picks.append(pick)

        df = pd.DataFrame(dataset[picks])
        print(df.to_string())

        return df

    randoms = show_random_elements(timit['test'])

    import soundfile as sf
    example = randoms.iloc[0]
    speech_array, sampling_rate = sf.read(example['file'])

    import sounddevice as sd
    sd.play(speech_array, sampling_rate)
    print(speech_array.shape, example['text'])
    sd.wait()

    # # load pretrained model
    model_id = "jonatasgrosman/wav2vec2-large-english"
    model_id = "facebook/wav2vec2-large-960h"

    asr = Wav2Vec2ASR(model_id, 16000)
    print(asr.speech_to_text(speech_array, sampling_rate))
