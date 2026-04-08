"""rename users table to members

Revision ID: 0f156f322634
Revises: 1cf99d3e954c
Create Date: 2026-04-08 13:49:41.715689

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f156f322634"
down_revision: Union[str, Sequence[str], None] = "1cf99d3e954c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("reveiwer_skills", "reviewer_skills")


def downgrade() -> None:
    op.rename_table("reviewer_skills", "reveiwer_skills")
