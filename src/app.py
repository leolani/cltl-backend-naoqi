import logging.config
import time

logging.config.fileConfig('config/logging.config')

import json
from types import SimpleNamespace

from cltl.combot.infra.config.local import LocalConfigurationContainer
from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.event.kombu import KombuEventBus
from cltl.combot.infra.resource.threaded import ThreadedResourceContainer
from event.consumer import TemplateWorker
from kombu.serialization import register

from event.producer import Producer


logger = logging.getLogger(__name__)

LocalConfigurationContainer.load_configuration()

class ApplicationContainer(ThreadedResourceContainer, LocalConfigurationContainer):
    logger.info("Initialized ApplicationContainer")

    @property
    @singleton
    def event_bus(self):
        register('cltl-json',
                 lambda x: json.dumps(x, default=vars),
                 lambda x: json.loads(x, object_hook=lambda d: SimpleNamespace(**d)),
                 content_type='application/json',
                 content_encoding='utf-8')
        return KombuEventBus('cltl-json', self.config_manager)

    @property
    @singleton
    def consumer(self):
        return TemplateWorker(None, self.event_bus, self.resource_manager, self.config_manager)

    @property
    @singleton
    def producer(self):
        return Producer(self.event_bus, self.config_manager)


class Application(ApplicationContainer):
    def __init__(self, args):
        self._args = args

    def run(self):
        if self._args.producer:
            self.producer.start()
        elif self._args.consumer:
            self.consumer.start()
        else:
            while True:
                logger.info("Ping")
                time.sleep(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--producer',
                        help='Run event producer',
                        action='store_true', required=False)
    parser.add_argument('-c', '--consumer',
                        help='Run event consumer',
                        action='store_true', required=False)

    Application(parser.parse_args()).run()
