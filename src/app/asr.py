import logging
from types import SimpleNamespace

import numpy as np
from flask import Flask, Response, request

from cltl.asr.wav2vec_asr import Wav2Vec2ASR

logger = logging.getLogger(__name__)


CONTENT_TYPE_SEPARATOR = ';'


def asr_app(model_id, sampling_rate=16000, storage=None):
    app = Flask(__name__)

    asr = Wav2Vec2ASR(model_id, sampling_rate, storage=storage)

    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        content_type = request.headers['content-type'].split(CONTENT_TYPE_SEPARATOR)
        if not content_type[0].strip() == 'audio/L16' or len(content_type) != 4:
            # Only support 16bit audio for now
            raise ValueError(f"Unsupported content type {request.headers['content-type']}, "
                             "expected audio/L16 with rate, channels and frame_size paramters")

        parameters = SimpleNamespace(**{p.split('=')[0].strip(): int(p.split('=')[1].strip())
                                        for p in content_type[1:]})

        logger.debug("Transcribe from (%s, %s)", content_type[0], parameters)

        # Two bytes per sample for 16bit audio
        content = np.frombuffer(request.data, np.int16)
        logger.debug("Transcribed speech [%s, %s]", content.shape, parameters.channels)
        content = content.reshape(content.shape[0] // parameters.channels, parameters.channels)
        transcript = asr.speech_to_text(content, parameters.rate)

        logger.debug("Transcribed speech (%s) to: %s", content.shape, transcript)

        return Response("{'transcript': " + str(transcript) + "}", mimetype='application/json')

    @app.after_request
    def set_cache_control(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    return app
