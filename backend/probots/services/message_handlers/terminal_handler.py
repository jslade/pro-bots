import structlog

from ...models.all import Message, Session
from ..dispatcher import Dispatcher
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class TerminalHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("terminal", "input", self.handle_input)

    def handle_input(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        dispatcher.send(
            session, "terminal", "output", {"output": message.data.get("input", "")}
        )
