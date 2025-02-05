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

    password: Mapped[str] = mapped_column(DB.String(40), nullable=False)
    display_name: Mapped[str] = mapped_column(DB.String(40), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=True, onupdate=datetime.now(tz=UTC)
    )
    changed_at: Mapped[datetime] = mapped_column(DB.DateTime, nullable=True)

    programs: Mapped[list["Program"]] = relationship("Program", back_populates="user")

    def current_program(self) -> Optional["Program"]:
        return Program.for_user(self, None)
