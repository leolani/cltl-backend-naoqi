import logging

import flask
import numpy as np
from flask import Flask, Response, stream_with_context, jsonify, request
from flask import g as app_context
from flask.json import JSONEncoder

from cltl.naoqi.api.camera import Image
from cltl.naoqi.audio_source import NAOqiMicrophone
from cltl.naoqi.image_source import NAOqiCamera
from cltl.naoqi.tts_output import NAOqiTextToSpeech

logger = logging.getLogger(__name__)


# TODO move to common util in combot
class NumpyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Image):
            return vars(obj)

        return super(NumpyJSONEncoder, self).default(obj)


class BackendServer:
    def __init__(self, mic, camera, tts):
        self._mic = mic
        self._camera = camera
        self._tts = tts

        self._app = None
        self._image_source = None
        self._audio_source = None

    @classmethod
    def for_session(cls, naoqi_session, sampling_rate, channels, frame_size, audio_index, audio_buffer,
                 camera_resolution, camera_rate, tts_speed):
        mic = NAOqiMicrophone(naoqi_session, sampling_rate, channels, frame_size, audio_index, audio_buffer) \
              if sampling_rate > 0 else None
        camera = NAOqiCamera(naoqi_session, camera_resolution, camera_rate) \
                 if camera_rate > 0 else None
        tts = NAOqiTextToSpeech(naoqi_session, tts_speed)

        return cls(mic, camera, tts)

    @property
    def app(self):
        if self._app is not None:
            return self._app

        self._app = Flask(__name__)
        self._app.json_encoder = NumpyJSONEncoder

        @self._app.route("/image")
        def capture():
            if not self._image_source:
                return Response(status=404)

            mimetype_with_resolution = "application/json; resolution=" + str(self._image_source.resolution.name)

            if flask.request.method == 'HEAD':
                return Response(200, headers={"Content-Type": mimetype_with_resolution})

            image = self._image_source.capture()

            response = jsonify(image)
            response.headers["Content-Type"] = mimetype_with_resolution

            return response

        @self._app.route("/audio")
        def stream_mic():
            if not self._audio_source:
                return Response(status=404)

            mic_stream = self._audio_source.start()

            def audio_stream():
                for frame in mic_stream:
                    yield frame.tobytes()

            # Store mic in (thread-local) app-context to be able to close it.
            app_context.mic = self._audio_source

            mime_type = "audio/L16; rate=" + str(self._mic.rate) + "; channels=" + \
                        str(self._mic.channels) + "; frame_size=" + str(self._mic.frame_size)
            stream = stream_with_context(audio_stream())

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
        try:
            if self._camera:
                self._image_source = self._camera.__enter__()
            if self._mic:
                self._audio_source = self._mic.__enter__()

            self.app.run(host=host, port=port)
        finally:
            if self._audio_source:
                self._audio_source.__exit__(None, None, None)
                self._audio_source = None
            if self._image_source:
                self.self._image_source.__exit__(None, None, None)
                self.self._image_source = None

    def _start_for_testing(self):
        """Method for testing only"""
        self._audio_source = self._mic.__enter__()
        self._image_source = self._camera.__enter__()