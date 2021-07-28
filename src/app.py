import json
import logging.config
from kombu.serialization import register
from types import SimpleNamespace

from chatui_app.app import Application, ApplicationContainer
from cltl.combot.infra.event.kombu import KombuEventBus
from cltl.combot.infra.event.memory import SynchronousEventBus

logging.config.fileConfig('config/logging.config')

from cltl.combot.infra.config.k8config import copy_k8_config, K8_CONFIG, K8_CONFIG_DIR
from cltl.combot.infra.config.local import load_configuration, LocalConfigurationManager, CONFIG, ADDITIONAL_CONFIGS
from cltl.combot.infra.resource.threaded import ThreadedResourceManager

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    configs = ADDITIONAL_CONFIGS
    try:
        copy_k8_config(K8_CONFIG_DIR, K8_CONFIG)
        configs += [K8_CONFIG]
    except OSError:
        logger.exception("Could not load kubernetes config map from %s to %s", K8_CONFIG_DIR, K8_CONFIG)

    config = load_configuration(CONFIG, configs)
    run_local = config.get_config("cltl.chat-ui.events", "local")

    if run_local.lower() == 'true':
        application_container = ApplicationContainer(SynchronousEventBus(),
                                                     ThreadedResourceManager(),
                                                     LocalConfigurationManager(config))
        logger.info("Initialized Application with local event bus")
    else:
        register('cltl-json',
                 lambda x: json.dumps(x, default=vars),
                 lambda x: json.loads(x, object_hook=lambda d: SimpleNamespace(**d)),
                 content_type='application/json',
                 content_encoding='utf-8')

        configuration_manager = LocalConfigurationManager(config)
        application_container = ApplicationContainer(KombuEventBus('cltl-json', configuration_manager),
                                                     ThreadedResourceManager(),
                                                     configuration_manager)
        logger.info("Initialized ApplicationContainer with kombu event bus")

        Application(application_container).run()