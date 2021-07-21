import logging

import flask
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus, Event
from flask import jsonify, Response

from cltl.chatui.api import ResponseCache, Utterance


def create_app(response_cache: ResponseCache, event_bus: EventBus, config_manager: ConfigurationManager):
    config = config_manager.get_config("cltl.chat-ui.events")
    topic_utt = config.get("topic_utterance")

    app = flask.Flask(__name__)

    @app.route('/rest/chat/<chat_id>', methods=['GET', 'POST'])
    def utterances(chat_id: str):
        if flask.request.method == 'GET':
            try:
                utterances = response_cache.get_utterances(chat_id)
                responses = [utterance.text for utterance in utterances]

                return jsonify(responses)
            except ValueError:
                return Response(status=404)
        if flask.request.method == 'POST':
            speaker = flask.request.args.get('speaker', default="UNKNOWN", type=str)
            text = flask.request.get_data(as_text=True)
            utterance = Utterance(chat_id, speaker, text)
            event_bus.publish(topic_utt, Event.for_payload(utterance))

            return Response(status=200)

    @app.route('/rest/urlmap')
    def url_map():
        return str(app.url_map)

    return app
