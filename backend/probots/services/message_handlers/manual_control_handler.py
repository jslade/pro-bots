from typing import Optional

import structlog

from ...models.all import BaseSchema, Message, Session
from ...probotics.ops.all import Primitive
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from ..game.movement import MovementDir
from ..message_handlers.terminal_handler import TerminalOutput
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class MovementEvent(BaseSchema):
    move: Optional[str] = None
    turn: Optional[str] = None


class InspectionEvent(BaseSchema):
    x: int
    y: int


class ManualControlHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        mtype = "manual_control"
        dispatcher.register_handler(mtype, "movement", self.handle_movement)
        dispatcher.register_handler(mtype, "inspect", self.handle_inspect)

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
            ENGINE.mover.move(
                probot,
                dir=MovementDir.backward
                if event.move == "backward"
                else MovementDir.forward,
            )
        elif event.turn:
            ENGINE.mover.turn(probot, dir=event.turn)

    def handle_inspect(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        event = InspectionEvent(**message.data)

        probot = ENGINE.probot_for_session(session)
        if not probot:
            LOGGER.warning("no probot for session", session=session.id)
            return

        # LOGGER.info("manual inspection", ev=event, probot=probot)

        result = ENGINE.inspection.inspect(event.x, event.y)

        output = TerminalOutput(output=Primitive.output(result))
        dispatcher.send(session, "terminal", "output", output.as_msg())
