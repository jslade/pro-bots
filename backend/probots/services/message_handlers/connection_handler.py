from datetime import datetime
from typing import Optional

import structlog

from ...models.all import Message, Session, SessionType, User
from ...models.mixins.pydantic_base import BaseSchema
from ..dispatcher import Dispatcher
from ..game.engine import ENGINE
from .base import MessageHandler

LOGGER = structlog.get_logger(__name__)


class ConnectionRequest(BaseSchema):
    pass


class ConnectionResponse(BaseSchema):
    username: Optional[str]


class ConnectionHandler(MessageHandler):
    def register(self, dispatcher: Dispatcher) -> None:
        LOGGER.info(f"Registering {self.__class__.__name__}")
        dispatcher.register_handler("connection", "connected", self.handle_connected)

    def handle_connected(
        self, session: Session, message: Message, dispatcher: Dispatcher
    ) -> None:
        """This is the first message sent by the client session when it is connected"""
        request = ConnectionRequest(**message.data)

        LOGGER.info("Connection request received", session=session.id)
        session.connected_at = datetime.now()

        user = User.with_session_id(session.id)
        if session.type == SessionType.USER:
            if not user:
                raise Exception("No user matching that session")

            session.user = user

        response = ConnectionResponse(username=user.name if user else None)

        dispatcher.send(session, "connection", "accepted", response.as_msg())

        ENGINE.notify_of_current_state(session)
