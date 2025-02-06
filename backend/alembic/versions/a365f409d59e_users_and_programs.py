"""Users and programs

Create Date: 2025-02-05 15:48:15.544619

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a365f409d59e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("access_code", sa.String(length=10), nullable=False),
        sa.Column("display_name", sa.String(length=40), nullable=True),
        sa.Column("session_id", sa.String(length=40), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=True)
    op.create_index(op.f("ix_users_session_id"), "users", ["session_id"], unique=True)
    op.create_table(
        "programs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_programs_user_id"), "programs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_programs_user_id"), table_name="programs")
    op.drop_table("programs")
    op.drop_index(op.f("ix_users_session_id"), table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_table("users")
