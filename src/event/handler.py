from dataclasses import dataclass

import asyncapi
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus
from cltl.combot.infra.event.api import EventMetadata, Event
from cltl.combot.infra.resource import ResourceManager
from cltl.combot.infra.topic_worker import TopicWorker

from cltl.demo.api import ExampleInput
from cltl.demo.implementation import DummyExampleComponent


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


TOPICS = ["cltl.topic.one", "cltl.topic.two"]


class TemplateWorker(TopicWorker):
    def __init__(self, name: str, event_bus: EventBus, resource_manager: ResourceManager,
                 config_manager: ConfigurationManager) -> None:
        config = config_manager.get_config("template.config")
        self._name = name if name else config.get("name")
        super().__init__(TOPICS, event_bus, interval=0, name=name, resource_manager=resource_manager,
                         requires=[], provides=[])
        # super().__init__(TOPICS, event_bus, interval=0, name=name, resource_manager=resource_manager,
        #                  requires=TOPICS, provides=["cltl.topic.template"])

    def process(self, event: Event) -> None:
        if "cltl.topic.one" == event.metadata.topic:
            print(f"Received cltl.topic.one event {event.id}")
        elif "cltl.topic.two" == event.metadata.topic:
            print(f"Received cltl.topic.two event {event.id}")

        result = DummyExampleComponent().foo_bar(event.payload)

        self.event_bus.publish("cltl.topic.template", Event(result, None))
