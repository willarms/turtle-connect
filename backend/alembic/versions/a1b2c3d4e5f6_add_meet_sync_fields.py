"""add meet sync fields

Revision ID: a1b2c3d4e5f6
Revises: fc4c2442870e
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fc4c2442870e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('groups', sa.Column('meet_host_user_id', sa.Integer(), nullable=True))
    op.add_column('activities', sa.Column('meet_conference_id', sa.String(), nullable=True))
    op.create_index('ix_activities_meet_conference_id', 'activities', ['meet_conference_id'])


def downgrade() -> None:
    op.drop_index('ix_activities_meet_conference_id', table_name='activities')
    op.drop_column('activities', 'meet_conference_id')
    op.drop_column('groups', 'meet_host_user_id')
