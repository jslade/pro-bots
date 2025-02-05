from datetime import UTC, datetime

from sqlalchemy.orm import Mapped, mapped_column

from ...db import DB


class Timestamped:
    updated_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=True, onupdate=datetime.now(tz=UTC)
    )
    changed_at: Mapped[datetime] = mapped_column(DB.DateTime, nullable=True)
