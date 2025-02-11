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

        # TODO: Just for testing
        if input.input == "move":
            from ..game.engine import ENGINE

            probot = ENGINE.probots[0]
            ENGINE.mover.move(probot)
            return

        # TODO: Just for testing
        if input.input.startswith("turn"):
            from ..game.engine import ENGINE

            dir = input.input.split()[1]
            probot = ENGINE.probots[0]
            ENGINE.mover.turn(probot, dir)
            return

        # For now, just echo the input
        output = TerminalOutput(output=input.input)
        dispatcher.send(session, "terminal", "output", output.model_dump())
