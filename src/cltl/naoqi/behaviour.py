import logging

from cltl.naoqi.spi.behaviour import BehaviourController, Behaviour

logger = logging.getLogger(__name__)


_NAOQI_BEHAVIOR = {
    Behaviour.AUTONOMOUS_VISUAL_FEEDBACK: "AutonomousBlinking"
}


class NAOqiBehaviourController(BehaviourController):
    """
    NAOqi Behavior.

    Parameters
    ----------
    session: qi.Session
        Qi Application Session.
    """
    SERVICE = "ALAutonomousLife"

    def __init__(self, session):
        # Subscribe to NAOqi Text to Speech Service
        self._service = session.service(NAOqiBehaviourController.SERVICE)
        logger.debug("Booted")

    def start(self, behaviour):
        self._service.setAutonomousAbilityEnabled(_NAOQI_BEHAVIOR[behaviour], True)

    def stop(self, behaviour):
        self._service.setAutonomousAbilityEnabled(_NAOQI_BEHAVIOR[behaviour], False)
