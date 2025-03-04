from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import PKId, UniquelyNamed

if TYPE_CHECKING:
    from .program import Program

LOGGER = structlog.get_logger(__name__)


class User(DB.Model, PKId, UniquelyNamed):
    __tablename__ = "users"

    access_code: Mapped[str] = mapped_column(DB.String(10), nullable=False)
    display_name: Mapped[str] = mapped_column(DB.String(40), nullable=True)

    session_id: Mapped[str] = mapped_column(DB.String(40), nullable=True, index=True)
    admin: Mapped[bool] = mapped_column(DB.Boolean, nullable=False, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=True, onupdate=datetime.now(tz=UTC)
    )
    changed_at: Mapped[datetime] = mapped_column(DB.DateTime, nullable=True)

    programs: Mapped[list["Program"]] = relationship("Program", back_populates="user")

    color_head: Mapped[str] = mapped_column(DB.String(20), nullable=True)
    color_tail: Mapped[str] = mapped_column(DB.String(20), nullable=True)
    color_body: Mapped[str] = mapped_column(DB.String(20), nullable=True)

    @property
    def current_program(self) -> Optional["Program"]:
        from .program import Program

        return Program.for_user(self, None)

    @classmethod
    def with_session_id(cls, session_id: str) -> Optional["User"]:
        return cls.query.filter_by(session_id=session_id).first()
