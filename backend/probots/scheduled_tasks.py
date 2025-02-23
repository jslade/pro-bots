import structlog
from flask_apscheduler import APScheduler

from .app import APP

LOGGER = structlog.get_logger(__name__)

SCHEDULER = APScheduler()
SCHEDULER.init_app(APP)


# @SCHEDULER.task(trigger="interval", seconds=60)
def periodically_ping() -> None:
    from .services.ping_service import PingService

    LOGGER.info("ping")

    ping_service = PingService()

    ping_service.ping_all()


@SCHEDULER.task(trigger="interval", seconds=60)
def cleanup_stale_sessions() -> None:
    from .services.monitor import MONITOR

    MONITOR.cleanup_stale_sessions()


@SCHEDULER.task(trigger="interval", seconds=60)
def save_user_changes() -> None:
    from .services.game.engine import ENGINE

    ENGINE.save_user_changes()
