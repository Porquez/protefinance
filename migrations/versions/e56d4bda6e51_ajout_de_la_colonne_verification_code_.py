"""Ajout de la colonne verification_code dans User

Revision ID: e56d4bda6e51
Revises: de743320019d
Create Date: 2024-10-30 20:05:45.713192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e56d4bda6e51'
down_revision = 'de743320019d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('verification_code', sa.String(length=6), nullable=True))

