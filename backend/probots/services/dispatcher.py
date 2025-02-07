from probots.models.message import Message
from probots.models.session import Session
from probots.models.websocket import WebSocket


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
        try:
            ws = self.websockets[session.id]
        except KeyError:
            return

        message = Message(
            type=mtype,
            event=event,
            session_id=session.id,
            data=data,
        )
        ws.send(message.model_dump_json())


DISPATCHER = Dispatcher()
