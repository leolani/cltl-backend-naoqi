import logging.config
logging.config.fileConfig('config/logging.config')

import json
import sys
from types import SimpleNamespace

import connexion
import event.handler
import rest.endpoint
from cltl.combot.infra.config.local import LocalConfigurationContainer
from cltl.combot.infra.di_container import singleton
from cltl.combot.infra.event.kombu import KombuEventBus
from cltl.combot.infra.resource.threaded import ThreadedResourceContainer
from cltl.demo.api import ExampleComponent
from event.handler import TemplateWorker
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
        return Producer(self.event_bus)


class Application(ApplicationContainer):
    def __init__(self, args):
        self._args = args

    def run(self):
        if self._args.data or self._args.file:
            if self._args.data:
                data_json = self._args.data
            elif self._args.file:
                with open(self._args.file) as f:
                    data_json = f.read()

            data = json.loads(data_json, object_hook=lambda d: SimpleNamespace(**d))
            sys.stdout.write(ExampleComponent().foo_bar(data))
        else:
            if self._args.producer:
                self.producer.start()
            if self._args.consumer:
                self.consumer.start()

            if self._args.rest or self._args.consumer:
                app = connexion.FlaskApp(__name__)
                if self._args.rest:
                    app.add_api(rest.endpoint.api.spec.to_dict())
                # if self._args.consumer:
                    # app.add_api(event.handler.api.spec.to_dict())

                # TODO Production WSGI server, see https://mikebridge.github.io/post/python-flask-kubernetes-3/
                # TODO Production WSGI server, see https://github.com/ram-ch/Building-microservices-with-docker-on-AWS
                app.run()

            if self._args.consumer:
                self.consumer.stop()


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
