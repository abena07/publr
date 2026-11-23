"""add google_user_id for google sign-in

Revision ID: b7c1e4a9d2f3
Revises: 1e11dae9381e
Create Date: 2026-11-23 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c1e4a9d2f3'
down_revision: Union[str, Sequence[str], None] = '1e11dae9381e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('google_user_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_google_user_id', 'users', ['google_user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_google_user_id', 'users', type_='unique')
    op.drop_column('users', 'google_user_id')
