"""create post_categories table

Revision ID: e8c745aa2c2d
Revises: 4021bf887b40
Create Date: 2026-03-24 17:35:55.232127

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8c745aa2c2d"
down_revision: str | Sequence[str] | None = "4021bf887b40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "post_categories",
        sa.Column("post_id", sa.UUID(), primary_key=True),
        sa.Column("category_id", sa.UUID(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )

    # add index
    op.create_index("ix_post_categories_post_id", "post_categories", ["post_id"])
    op.create_index(
        "ix_post_categories_category_id", "post_categories", ["category_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_post_categories_post_id", table_name="post_categories")
    op.drop_index("ix_post_categories_category_id", table_name="post_categories")
    op.drop_table("post_categories")
