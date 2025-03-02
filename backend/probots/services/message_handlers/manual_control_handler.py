from typing import Optional

import structlog

from ...models.all import Message, Session
from ...models.mixins.pydantic_base import BaseSchema
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class MovementEvent(BaseSchema):
    move: Optional[str] = None
    turn: Optional[str] = None


class ManualControlHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        mtype = "manual_control"
        dispatcher.register_handler(mtype, "movement", self.handle_movement)

    def handle_movement(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        event = MovementEvent(**message.data)

        probot = ENGINE.probot_for_session(session)
        if not probot:
            LOGGER.warning("no probot for session", session=session.id)
            return

        # LOGGER.info("manual movement", ev=event, probot=probot)

        if event.move:
            ENGINE.mover.move(probot, backward=event.move == "backward")
        elif event.turn:
            ENGINE.mover.turn(probot, dir=event.turn)
