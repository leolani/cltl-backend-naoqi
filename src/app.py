import logging.config

from cltl.combot.infra.event.kombu import KombuEventBusContainer
from cltl.combot.infra.event.memory import SynchronousEventBusContainer
from cltl.combot.infra.topic_worker import TopicWorker
from flask import Flask

from cltl.chatui.api import Chat
from cltl.chatui.memory import MemoryChat
from rest.endpoint import create_app

logging.config.fileConfig('config/logging.config')

from cltl.combot.infra.config.k8config import K8LocalConfigurationContainer
from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.resource.threaded import ThreadedResourceContainer
from event.consumer import ResponseWorker

logger = logging.getLogger(__name__)

K8LocalConfigurationContainer.load_configuration()
run_local = K8LocalConfigurationContainer.get_config("cltl.chat-ui.events", "local")


if run_local.lower() == 'true':
    class ApplicationContainer(SynchronousEventBusContainer, ThreadedResourceContainer, K8LocalConfigurationContainer):
        logger.info("Initialized ApplicationContainer with local event bus")
else:
    class ApplicationContainer(KombuEventBusContainer, ThreadedResourceContainer, K8LocalConfigurationContainer):
        logger.info("Initialized ApplicationContainer with kombu event bus")


class Application(ApplicationContainer):
    @property
    @singleton
    def chat(self) -> Chat:
        return MemoryChat()

    @property
    @singleton
    def consumer(self) -> TopicWorker:
        return ResponseWorker(self.chat, self.event_bus, self.resource_manager, self.config_manager)

    @property
    @singleton
    def backend(self) -> Flask:
        return create_app(self.chat, self.event_bus, self.config_manager)

    def run(self):
        self.consumer.start()
        self.backend.run(host="0.0.0.0", threaded=False, processes=1)


if __name__ == '__main__':
    Application().run()
