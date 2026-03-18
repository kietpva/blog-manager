"""create users table

Revision ID: b23b1bafdee8
Revises: efc5cee46fe0
Create Date: 2026-03-17 16:44:50.417350

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b23b1bafdee8"
down_revision: Union[str, Sequence[str], None] = "efc5cee46fe0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("auth_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            postgresql.ENUM("admin", "user", name="user_role", create_type=False),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_unique_constraint("uq_users_auth_id", "users", ["auth_id"])
    op.create_index("ix_users_auth_id", "users", ["auth_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_users_auth_id", table_name="users")
    op.drop_constraint("uq_users_auth_id", "users", type_="unique")
    op.drop_table("users")
