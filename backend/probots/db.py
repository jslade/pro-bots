import os
import flask_sqlalchemy.session

from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic
from sqlalchemy.orm import scoped_session
from typing import TypeAlias

from .app import APP

APP.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/probots"
)
DB = SQLAlchemy(APP)

DbSession: TypeAlias = scoped_session[flask_sqlalchemy.session.Session]

alembic = Alembic()
alembic.init_app(APP)
