from datetime import datetime
from typing import Optional

import structlog

from ..models.websocket import WebSocket
from ..models.session import Session, SessionType

LOGGER = structlog.get_logger(__name__)


class SessionService:
    """Keeps track of all of the sessions. A session is created when a user/client
    exists, but it does not necessarily go away if the client disconnects.
    Because of the tenouous nature of websocket connects, it allows for
    disconnecting and then reconnecting, resuming the session."""

    def __init__(self):
        self.all_sessions = {}
        self.user_sessions = {}
        self.server_sessions = {}

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.all_sessions.get(session_id, None)

    def add_session(self, session_id: str) -> Session:
        if existing := self.get_session(session_id):
            return existing

        session_type = Session.type_from_id(session_id)

        session = Session(type=session_type, id=session_id, created_at=datetime.now())
        self.all_sessions[session.id] = session

        match session.type:
            case SessionType.USER:
                self.user_sessions[session.id] = session
            case SessionType.SERVER:
                self.server_sessions[session.id] = session

        return session

    def remove_session(self, session: Session) -> None:
        del self.all_sessions[session.id]

        match session.type:
            case SessionType.USER:
                del self.user_sessions[session.id]
            case SessionType.SERVER:
                del self.server_sessions[session.id]

    def connected(self, session: Session, ws: WebSocket) -> None:
        session.ws = ws
        session.connected_at = datetime.now()
        session.disconnected_at = None

    def disconnected(self, session: Session) -> None:
        session.ws = None
        session.disconnected_at = datetime.now()

    def for_each_session(self):
        for session in self.all_sessions.values():
            yield session

    def for_each_user_session(self):
        for session in self.user_sessions.values():
            yield session

    def for_each_server_session(self):
        for session in self.server_sessions.values():
            yield session


SESSIONS = SessionService()
