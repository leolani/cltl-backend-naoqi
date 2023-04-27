import enum
import logging

logger = logging.getLogger(__name__)


class Behaviour(enum.Enum):
    # TO BE EXTENDED
    AUTONOMOUS_VISUAL_FEEDBACK = 1


class BehaviourController:
    def start(self, behaviour):
        raise NotImplementedError()

    def stop(self, behaviour):
        raise NotImplementedError()
