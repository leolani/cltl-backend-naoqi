from dataclasses import dataclass

import logging.config

from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import EventBus
from cltl.combot.infra.resource import ResourceManager

logging.config.fileConfig('config/logging.config')
logger = logging.getLogger(__name__)

from cltl.chatui.memory import MemoryResponseCache
from .event.consumer import ResponseWorker
from .rest.endpoint import create_app


@dataclass
class ApplicationContainer:
    event_bus: EventBus
    resource_manager: ResourceManager
    config_manager: ConfigurationManager


class Application:
    def __init__(self, application_container: ApplicationContainer):
        cache = MemoryResponseCache()
        self.consumer = ResponseWorker(cache,
                                       application_container.event_bus,
                                       application_container.resource_manager,
                                       application_container.config_manager)
        self.web_app = create_app(cache,
                                  application_container.event_bus,
                                  application_container.config_manager)

    def run(self):
        logger.info("Starting application on host 0.0.0.0")
        self.consumer.start()
        self.web_app.run(host="0.0.0.0")
