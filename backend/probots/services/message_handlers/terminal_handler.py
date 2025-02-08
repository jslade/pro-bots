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

        # For now, just echo the input
        output = TerminalOutput(output=input.input)

        dispatcher.send(session, "terminal", "output", output.model_dump())
