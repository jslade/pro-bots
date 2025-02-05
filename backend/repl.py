import asyncio  # noqa: F401
import logging  # noqa: F401
from datetime import date, datetime, time, timedelta  # noqa: F401
from decimal import Decimal  # noqa: F401

import IPython

from probots.app import APP
from probots.db import DB, DbSession  # noqa: F401
from probots.models.all import *  # noqa: F403
from probots.services import *  # noqa: F403

# IPython setup -- enable auto-reload of source files
ipython = IPython.get_ipython()
ipython.run_line_magic(magic_name="load_ext", line="autoreload")
ipython.run_line_magic(magic_name="autoreload", line="2")


APP.app_context().push()
