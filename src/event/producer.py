import logging
from threading import Thread
from time import sleep

from cltl.combot.infra.event import EventBus
from cltl.combot.infra.event.api import Event

from cltl.demo.api import ExampleInput

logger = logging.getLogger(__name__)

# @dataclass
# class TemplateEvent:
#     id: str
#     payload: ExampleInput
#     metadata: EventMetadata
#
# dev_server = asyncapi.Server(
#     url='localhost',
#     protocol=asyncapi.ProtocolType.REDIS,
#     description='Development Broker Server',
# )
# message = asyncapi.Message(
#     name='templateEvent',
#     title='Template Event',
#     summary='Template Event description',
#     payload=TemplateEvent,
# )
# user_update_channel = asyncapi.Channel(
#     description='Topic for template events',
#     subscribe=asyncapi.Operation(
#         operation_id='receive_template_event', message=message,
#     ),
#     publish=asyncapi.Operation(message=message),
# )
#
# api = asyncapi.Specification(
#     info=asyncapi.Info(
#         title='User API', version='1.0.0', description='API to manage users',
#     ),
#     servers={'development': dev_server},
#     channels={'user/update': user_update_channel},
#     components=asyncapi.Components(messages={'UserUpdate': message}),
# )


TOPIC = "cltl.topic.one"


class Producer(Thread):
    def __init__(self, event_bus: EventBus, duration: int = 60) -> None:
        super().__init__(None, name="producer")
        self.__event_bus = event_bus
        self.__terminate = False
        self.__duration = duration

    def run(self) -> None:
        logger.info("Started producer")
        for i in range(self.__duration):
            if self.__terminate:
                return
            self.__event_bus.publish(TOPIC, Event(f"event{i}", ExampleInput(f"test {i}", 2), None))
            logger.debug("Sent event %s", i)
            sleep(1)

        logger.info("Stopped producer")

    def stop(self):
        self.__terminate = True
