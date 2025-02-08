import probots.controllers  # noqa: F401
import probots.db
import probots.models.all  # noqa: F401
from probots.app import APP, SOCK
from probots.scheduled_tasks import SCHEDULER
from probots.services.dispatcher import DISPATCHER
from probots.services.message_handlers.all import MESSAGE_HANDLERS

# Setup the various dispatch handlers
for handler in MESSAGE_HANDLERS:
    handler.register(DISPATCHER)

if __name__ == "__main__":
    SCHEDULER.start()
    APP.run(host="0.0.0.0", port=5001)
