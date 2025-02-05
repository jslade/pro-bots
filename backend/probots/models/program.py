from datetime import UTC, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional, Self

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB, DbSession
from .mixins import PKId, OptionallyNamed, Timestamped

if TYPE_CHECKING:
    from .user import User

LOGGER = structlog.get_logger(__name__)


class Program(DB.Model, PKId, OptionallyNamed, Timestamped):
    __tablename__ = "programs"

    user_id: Mapped[int] = mapped_column(
        DB.Integer,
        DB.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship("User", back_populates="programs")

    content: Mapped[str] = mapped_column(DB.String, nullable=False)

    @classmethod
    def for_user(cls, user: "User", name: Optional[str]) -> bool:
        query = cls.query.filter_by(user=user)
        if name is not None:
            return query.filter_by(name=name).first()
        else:
            # Most recently modified if not otherwise specified
            return query.order_by(cls.updated_at.desc()).first()
