import structlog

from ...models.all import Message, Session
from ..dispatcher import Dispatcher
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class ConnectionHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("connection", "connected", self.handle_connected)

    def handle_connected(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        """This is the first message sent by the client session when it is connected"""
        LOGGER.info("Connection request received", session=session.id)
        dispatcher.send(session, "connection", "accepted", {})
