"""empty message

Revision ID: 4edc7a993fb3
Revises: 746867e1d270
Create Date: 2026-05-09 10:41:50.567650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4edc7a993fb3'
down_revision: Union[str, Sequence[str], None] = '746867e1d270'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
