"""Ajout de la colonne email dans User

Revision ID: de743320019d
Revises: 92d055b2a0b7
Create Date: 2024-10-30 20:02:54.329218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de743320019d'
down_revision = '92d055b2a0b7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('email', sa.String(length=120), nullable=True))

def downgrade():
    op.drop_column('user', 'email')
