"""add to profilepic

Revision ID: 4e5a158f4fc0
Revises: 5a91463c88a2
Create Date: 2025-06-13 01:16:28.040814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5a158f4fc0'
down_revision: Union[str, None] = '5a91463c88a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
