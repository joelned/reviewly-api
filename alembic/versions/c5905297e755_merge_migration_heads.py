"""merge migration heads

Revision ID: c5905297e755
Revises: 0f156f322634, 87adf1e0d286
Create Date: 2026-04-08 16:39:07.489323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5905297e755'
down_revision: Union[str, Sequence[str], None] = ('0f156f322634', '87adf1e0d286')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
