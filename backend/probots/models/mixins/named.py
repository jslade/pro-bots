from typing import Optional, Self
from sqlalchemy import select

from ...db import DB, DbSession


class UniquelyNamed:
    name = DB.Column(DB.String(60), nullable=False, index=True, unique=True)

    @classmethod
    def with_name(
        cls, name: str, db_session: Optional[DbSession] = None
    ) -> Optional[Self]:
        db_session = db_session or DB.session
        stmt = select(cls).where(cls.name == name)
        return db_session.scalar(stmt)


class OptionallyNamed:
    name = DB.Column(DB.String(60), nullable=True)
