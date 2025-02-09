from datetime import datetime, timedelta

import probots.controllers  # noqa: F401
import probots.db
import probots.models.all  # noqa: F401
from probots.app import APP
from probots.scheduled_tasks import SCHEDULER
from probots.services.dispatcher import DISPATCHER
from probots.services.message_handlers.all import MESSAGE_HANDLERS
from probots.services.monitor import MONITOR

DEBUG = True


def do_setup() -> None:
    # Setup the various dispatch handlers
    for handler in MESSAGE_HANDLERS:
        handler.register(DISPATCHER)

    # Initialize the game monitor that oversees the whole operation
    # This ends up starting a background thread that runs separately
    # from the flask stuff happening in the main thread
    MONITOR.run()


# Flask debug causes a process fork, and it takes a bit to happen.
# If we call the startup task immediately, it's duplicated in the forked
# process. But doing it as a deferred task ensures it happens post-fork

SCHEDULER.add_job(
    id="post_fork_setup",
    func=do_setup,
    trigger="date",
    run_date=datetime.now() + timedelta(seconds=1),
)

if __name__ == "__main__":
    SCHEDULER.start()
    APP.run(host="0.0.0.0", port=5001)
