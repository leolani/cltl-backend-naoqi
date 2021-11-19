import logging

import flask
import numpy as np
from flask import Flask, Response, stream_with_context, jsonify, request
from flask import g as app_context
from flask.json import JSONEncoder

from cltl.naoqi.audio_source import NAOqiAudioSource
from cltl.naoqi.image_source import NAOqiImageSource
from cltl.naoqi.tts_output import NAOqiTextToSpeech

logger = logging.getLogger(__name__)


# TODO move to common util in combot
class NumpyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return super().default(obj)


class BackendServer:
    def __init__(self, naoqi_session, sampling_rate, channels, frame_size, audio_index, audio_buffer,
                 camera_resolution, camera_rate, tts_speed):
        self._mic = NAOqiAudioSource(naoqi_session, sampling_rate, channels, frame_size, audio_index, audio_buffer)
        self._camera = NAOqiImageSource(naoqi_session, camera_resolution, camera_rate)
        self._tts = NAOqiTextToSpeech(naoqi_session, tts_speed)

        self._sampling_rate = sampling_rate
        self._channels = channels
        self._frame_size = frame_size

        self._app = None

    @property
    def app(self):
        if self._app is not None:
            return self._app

        self._app = Flask(__name__)
        self._app.json_encoder = NumpyJSONEncoder

        # TODO Change to /image here and in the backend
        @self._app.route("/video")
        def capture():
            mimetype_with_resolution = "application/json; resolution=" + str(self._camera.resolution.name)

            if flask.request.method == 'HEAD':
                return Response(200, headers={"Content-Type": mimetype_with_resolution})

            with self._camera as camera:
                image = camera.capture()

            response = jsonify(image)
            response.headers["Content-Type"] = mimetype_with_resolution

            return response

        @self._app.route("/audio")
        def stream_mic():
            def audio_stream(mic):
                with self._mic as mic_stream:
                    for frame in mic_stream:
                        yield frame

            # Store mic in (thread-local) app-context to be able to close it.
            app_context.mic = self._mic

            mime_type = "audio/L16; rate=" + str(self._sampling_rate) + "; channels=" + str(self._channels) + "; frame_size=" + str(self._frame_size)
            stream = stream_with_context(audio_stream(self._mic))

            return Response(stream, mimetype=mime_type)

        # TODO support language and animations
        @self._app.route("/text", methods=['POST'])
        def tts():
            text = request.data
            self._tts.consume(text)

            return Response(status=200)

        @self._app.after_request
        def set_cache_control(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response

        @self._app.teardown_request
        def close_mic(_=None):
            if "mic" in app_context:
                app_context.mic.stop()

        return self._app

    def run(self, host, port):
        self.app.run(host=host, port=port)
