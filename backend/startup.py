import probots.controllers  # noqa: F401
import probots.db
import probots.models.all  # noqa: F401
from probots.app import APP, SOCK
from probots.scheduled_tasks import SCHEDULER

if __name__ == "__main__":
    SCHEDULER.start()
    APP.run(host="0.0.0.0", port=5001)
