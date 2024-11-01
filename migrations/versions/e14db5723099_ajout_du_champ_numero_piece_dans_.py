"""Ajout du champ numero_piece dans Operation

Revision ID: e14db5723099
Revises: 
Create Date: 2024-10-10 15:58:46.052849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e14db5723099'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('operation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_piece', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('operation', schema=None) as batch_op:
        batch_op.drop_column('numero_piece')

    # ### end Alembic commands ###
