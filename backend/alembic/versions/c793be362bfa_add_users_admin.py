"""add users.admin

Create Date: 2025-03-04 00:06:16.997365

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c793be362bfa"
down_revision: Union[str, None] = "6d3427d14748"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("admin", sa.Boolean(), nullable=False, server_default="false")
    )


def downgrade() -> None:
    op.drop_column("users", "admin")
