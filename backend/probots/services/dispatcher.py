import structlog
from typing import Optional, TypeAlias, Callable

from probots.models.message import Message
from probots.models.session import Session
from probots.models.websocket import WebSocket

LOGGER = structlog.get_logger(__name__)

HandlerKey: TypeAlias = tuple[str, str]
HandlerType: TypeAlias = Callable[[Session, Message, "Dispatcher"], None]


class Dispatcher:
    """Handles routing messages to the correct service."""

    def __init__(self) -> None:
        self.sessions = {}
        self.websockets = {}
        self.handlers: dict[HandlerKey, HandlerType] = {}

    def add_connection(self, session: Session, ws: WebSocket) -> None:
        self.sessions[session.id] = session
        self.websockets[session.id] = ws

    def remove_connection(self, session: Session, ws: WebSocket) -> None:
        try:
            del self.sessions[session.id]
        except KeyError:
            pass
        try:
            del self.websockets[session.id]
        except KeyError:
            pass

    def send(self, session: Session, mtype: str, event: str, data: dict) -> None:
        """Immediately send a message out via the session's websocket."""
        try:
            ws = self.websockets[session.id]
        except KeyError:
            return

        try:
            message = Message(
                type=mtype,
                event=event,
                session_id=session.id,
                data=data,
            )
            ws.send(message.model_dump_json())
        except Exception as e:
            LOGGER.warn("Failed to send message", session=session.id, error=e)
            self.remove_connection(session, ws)

    def register_handler(
        self, mtype: str, event: Optional[str], handler: HandlerType
    ) -> None:
        """Register a handler for a specific message type and event."""
        self.handlers[(mtype, event)] = handler

    def receive(self, session: Session, message: Message) -> None:
        """Called when a message is received from a session's websocket."""
        LOGGER.info("Received message", session=session.id, message=message)

        handled = False

        if type_event_handler := self.handlers.get((message.type, message.event)):
            self.dispatch(session, message, type_event_handler)
            handled = True
        if type_handler := self.handlers.get((message.type, None)):
            self.dispatch(session, message, type_handler)
            handled = True

        if not handled:
            LOGGER.warning(
                "No handler for message",
                session=session.id,
                key=(message.type, message.event),
            )

    def dispatch(self, session: Session, message: Message, handler: HandlerType) -> None:
        try:
            handler(session, message, self)
        except Exception as e:
            LOGGER.exception(
                "Failed to dispatch message", error=e, session=session.id, message=message
            )


DISPATCHER = Dispatcher()
