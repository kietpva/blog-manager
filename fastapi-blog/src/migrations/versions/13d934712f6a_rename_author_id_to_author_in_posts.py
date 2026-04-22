"""rename author_id to author in posts

Revision ID: 13d934712f6a
Revises: 41dc78ff6b6a
Create Date: 2026-04-22 14:35:14.027354

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "13d934712f6a"
down_revision: str | Sequence[str] | None = "41dc78ff6b6a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema by renaming column 'author_id' to 'author' in 'posts' table."""
    op.alter_column(
        "posts",
        "author_id",
        new_column_name="author",
    )


def downgrade() -> None:
    """Downgrade schema by renaming column 'author' back to 'author_id' in 'posts' table."""
    op.alter_column(
        "posts",
        "author",
        new_column_name="author_id",
    )
