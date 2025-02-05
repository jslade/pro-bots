from typing import TYPE_CHECKING, Optional

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import PKId, UniquelyNamed

if TYPE_CHECKING:
    from .hashing_schedule import HashingSchedule

LOGGER = structlog.get_logger(__name__)


class AsicProfile(DB.Model, PKId, UniquelyNamed):
    __tablename__ = "asic_profiles"

    schedule_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("hashing_schedules.id"), nullable=True
    )
    schedule: Mapped[Optional["HashingSchedule"]] = relationship("HashingSchedule")
