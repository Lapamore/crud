"""add subscriptions

Revision ID: a1b2c3d4e5f6
Revises: 0001
Create Date: 2025-12-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f47ac10b58cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('subscription_key', sa.String(), nullable=True))
    op.create_table('subscribers',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('subscriber_id', sa.BigInteger(), nullable=False),
        sa.Column('author_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subscriber_id', 'author_id', name='ux_sub')
    )


def downgrade() -> None:
    op.drop_table('subscribers')
    op.drop_column('users', 'subscription_key')
