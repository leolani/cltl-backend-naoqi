import logging
from collections import namedtuple
from dataclasses import dataclass

import asyncapi
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus
from cltl.combot.infra.event.api import EventMetadata, Event
from cltl.combot.infra.resource import ResourceManager
from cltl.combot.infra.topic_worker import TopicWorker

from cltl.demo.api import ExampleInput
from cltl.demo.implementation import DummyExampleComponent

logger = logging.getLogger(__name__)


@dataclass
class TemplateEvent:
    id: str
    payload: ExampleInput
    metadata: EventMetadata

dev_server = asyncapi.Server(
    url='localhost',
    protocol=asyncapi.ProtocolType.REDIS,
    description='Development Broker Server',
)
message = asyncapi.Message(
    name='templateEvent',
    title='Template Event',
    summary='Template Event description',
    payload=TemplateEvent,
)
user_update_channel = asyncapi.Channel(
    description='Topic for template events',
    subscribe=asyncapi.Operation(
        operation_id='receive_template_event', message=message,
    ),
    publish=asyncapi.Operation(message=message),
)

api = asyncapi.Specification(
    info=asyncapi.Info(
        title='User API', version='1.0.0', description='API to manage users',
    ),
    servers={'development': dev_server},
    channels={'user/update': user_update_channel},
    components=asyncapi.Components(messages={'UserUpdate': message}),
)


class TemplateWorker(TopicWorker):
    def __init__(self, name: str, event_bus: EventBus, resource_manager: ResourceManager,
                 config_manager: ConfigurationManager) -> None:
        config = config_manager.get_config("cltl.demo.config")
        self._name = name if name else config.get("name")
        event_config = config_manager.get_config("cltl.demo.events")
        self.topics = namedtuple("topics", ["topic_in", "topic_out"])(
            event_config.get("consumer_topic_in"), event_config.get("consumer_topic_out"))
        super().__init__([self.topics.topic_in], event_bus, interval=0, name=name, resource_manager=resource_manager,
                         requires=[], provides=[self.topics.topic_out])

    def process(self, event: Event) -> None:
        if self.topics.topic_in == event.metadata.topic:
            logger.info("Received %s event %s", self.topics.topic_in, event.id)
        else:
            logger.info("Received unhandled %s event %s", self.topics.topic_in, event.id)

        result = DummyExampleComponent().foo_bar(event.payload)

        self.event_bus.publish(self.topics.topic_out, Event.for_payload(result))
