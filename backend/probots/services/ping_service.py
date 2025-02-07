import structlog

from probots.models.session import Session
from .dispatcher import DISPATCHER
from .session_service import SessionService, SESSIONS

LOGGER = structlog.get_logger(__name__)


class PingService:
    def __init__(self, session_service: SessionService = SESSIONS):
        self.session_service = session_service

    def ping_all(self):
        for session in self.session_service.for_each_session():
            self.ping_session(session)

    def ping_session(self, session: Session):
        LOGGER.info("ping session", session=session.id)

        DISPATCHER.send(session, "connection", "ping", {})
