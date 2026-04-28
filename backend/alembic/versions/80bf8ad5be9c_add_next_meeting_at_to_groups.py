"""add next_meeting_at to groups

Revision ID: 80bf8ad5be9c
Revises: a1f8e9322f3d
Create Date: 2026-04-27 23:22:54.342988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80bf8ad5be9c'
down_revision: Union[str, None] = 'a1f8e9322f3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('groups', sa.Column('next_meeting_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('groups', 'next_meeting_at')
