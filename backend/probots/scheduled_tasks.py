import structlog
from flask_apscheduler import APScheduler

from .app import APP

LOGGER = structlog.get_logger(__name__)

SCHEDULER = APScheduler()
SCHEDULER.init_app(APP)


@SCHEDULER.task("interval", id="periodically_ping", seconds=60)
def periodically_ping() -> None:
    LOGGER.info("ping test")
