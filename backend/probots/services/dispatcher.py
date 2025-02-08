import structlog

from probots.models.message import Message
from probots.models.session import Session
from probots.models.websocket import WebSocket

LOGGER = structlog.get_logger(__name__)


class Dispatcher:
    def __init__(self) -> None:
        self.sessions = {}
        self.websockets = {}

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

    def receive(self, session: Session, message: Message) -> None:
        """Called when a message is received from a session's websocket."""
        LOGGER.info("Received message", session=session.id, message=message)

        if (message.type, message.event) == ("terminal", "input"):
            self.send(session, "terminal", "output", {"output": message.data["input"]})


DISPATCHER = Dispatcher()
