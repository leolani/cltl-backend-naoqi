import logging

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event.api import Event, EventBus
from cltl.combot.infra.resource import ResourceManager
from cltl.combot.infra.topic_worker import TopicWorker

from cltl.chatui.api import ResponseCache, Utterance

logger = logging.getLogger(__name__)


class ResponseWorker(TopicWorker):
    def __init__(self, response_cache: ResponseCache, event_bus: EventBus, resource_manager: ResourceManager, config_manager: ConfigurationManager,
                 name: str = None) -> None:
        self._response_cache = response_cache

        config = config_manager.get_config("cltl.chat-ui")
        self._name = name if name else config.get("name")
        self._agent = config.get("agent_id")

        event_config = config_manager.get_config("cltl.chat-ui.events")
        response_topic = event_config.get("topic_response")

        super().__init__([response_topic], event_bus, interval=0, name=name, resource_manager=resource_manager,
                         requires=[], provides=[])

    def process(self, event: Event) -> None:
        response = Utterance(event.payload.chat_id, self._agent, event.payload.text)
        self._response_cache.append(response)
