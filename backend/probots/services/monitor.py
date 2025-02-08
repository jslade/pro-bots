import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional

import structlog

from ..scheduled_tasks import SCHEDULER
from .session_service import SESSIONS
from .game.engine import ENGINE

LOGGER = structlog.get_logger(__name__)


class Monitor:
    def run(self) -> None:
        """This is the entry point for the monitor that is called during application
        startup. It will spawn a background thread where the monitor
        does the actual work."""
        LOGGER.info("Monitor startup")

        # Spawn the game engine in a separate thread
        self.game_thread = threading.Thread(target=ENGINE.run, daemon=True)
        self.game_thread.start()

    def cleanup_stale_sessions(self) -> None:
        now = datetime.now()
        max_disconnect_time = timedelta(minutes=2)
        for session in SESSIONS.for_each_session():
            if not session.disconnected_at:
                continue

            elapsed_since_disconnect = now - session.disconnected_at
            if elapsed_since_disconnect > max_disconnect_time:
                SCHEDULER.add_job(
                    id=f"cleanup_stale_session:{session.id}",
                    func=self.cleanup_stale_session,
                    args=(session.id,),
                )

    def cleanup_stale_session(self, session_id: str) -> None:
        session = SESSIONS.get_session(session_id)
        if not session:
            return

        if session.ws:
            LOGGER.error(
                "Can't remove stale session that is connected", session=session.id
            )
            return

        LOGGER.info("Removing stale session", session=session.id)
        SESSIONS.remove_session(session)


MONITOR = Monitor()
