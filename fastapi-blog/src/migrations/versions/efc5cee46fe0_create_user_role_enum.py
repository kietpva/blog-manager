"""create user role enum

Revision ID: efc5cee46fe0
Revises:
Create Date: 2026-03-17 16:43:07.786544

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "efc5cee46fe0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE user_role AS ENUM ('ADMIN', 'USER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TYPE IF EXISTS user_role CASCADE;")
