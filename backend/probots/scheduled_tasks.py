import structlog
from flask_apscheduler import APScheduler

from .app import APP
from .services.ping_service import PingService

LOGGER = structlog.get_logger(__name__)

SCHEDULER = APScheduler()
SCHEDULER.init_app(APP)


@SCHEDULER.task("interval", id="periodically_ping", seconds=60)
def periodically_ping() -> None:
    LOGGER.info("ping")

    ping_service = PingService()

    ping_service.ping_all()
