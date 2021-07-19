import logging

import flask
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus, Event
from flask import jsonify, Response

from cltl.chatui.api import Chat, Utterance


def create_app(chat: Chat, event_bus: EventBus, config_manager: ConfigurationManager):
    config = config_manager.get_config("cltl.chat-ui.events")
    topic_utt = config.get("topic_utterance")

    app = flask.Flask(__name__)

    @app.route('/rest/chat/<chat_id>', methods=['GET', 'POST'])
    def utterances(chat_id: str):
        if flask.request.method == 'GET':
            start = flask.request.args.get('start', type=int)
            end = flask.request.args.get('end', type=int)
            try:
                utterances = chat.get_utterances(chat_id, start=start, end=end)
                responses = [utterance.text for utterance in utterances]

                return jsonify(responses)
            except ValueError:
                return Response(status=404)
        if flask.request.method == 'POST':
            speaker = flask.request.args.get('speaker', default="UNKNOWN", type=str)
            text = flask.request.get_data(as_text=True)
            utterance = Utterance(chat_id, speaker, text)
            chat.append(utterance)
            logging.info("XXX publish")
            event_bus.publish(topic_utt, Event.for_payload(utterance))
            logging.info("XXX published")

            return ""

    @app.route('/rest/chat/<chat_id>/<seq>', methods=['GET'])
    def utterance(chat_id: str, seq: int) -> str:
        return chat.get_utterance(chat_id, seq).text

    @app.route('/rest/urlmap')
    def url_map():
        return str(app.url_map)

    return app
