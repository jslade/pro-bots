import structlog

from ...models.all import Message, Session
from ...models.mixins.pydantic_base import BaseSchema
from ..dispatcher import Dispatcher
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class TerminalInput(BaseSchema):
    input: str


class TerminalOutput(BaseSchema):
    output: str


class TerminalHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("terminal", "input", self.handle_input)

    def handle_input(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        input = TerminalInput(**message.data)

        # TODO: Just for testing
        if input.input == "map":
            from ..game.engine import ENGINE

            if grid := ENGINE.grid:
                output = TerminalOutput(output=grid.to_str())
            else:
                output = TerminalOutput(output="n/a")
            dispatcher.send(session, "terminal", "output", output.model_dump())
            return

        # TODO: Just for testing. Eventually this will be handled via probotics
        if input.input.startswith("move"):
            from ..game.engine import ENGINE

            backward = False
            bonus = 5

            words = input.input.split()
            if len(words) > 1:
                if words[1].startswith("back"):
                    backward = True
                    bonus = 10

            probot = ENGINE.probot_for_session(session)
            if probot:
                ENGINE.mover.move(probot, backward=backward, bonus=bonus)
            return

        # TODO: Just for testing. Eventually this will be handled via probotics
        if input.input.startswith("turn"):
            from ..game.engine import ENGINE

            words = input.input.split()
            if len(words) > 1:
                dir = words[1]

                probot = ENGINE.probot_for_session(session)
                if probot:
                    ENGINE.mover.turn(probot, dir=dir, bonus=3)
            return

        # For now, just echo the input
        output = TerminalOutput(output=f"??? {input.input}")
        dispatcher.send(session, "terminal", "output", output.model_dump())
