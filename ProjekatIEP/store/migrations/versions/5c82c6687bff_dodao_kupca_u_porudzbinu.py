"""Dodao kupca u porudzbinu

Revision ID: 5c82c6687bff
Revises: 60595c6de1d4
Create Date: 2022-08-11 08:05:14.307890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c82c6687bff'
down_revision = '60595c6de1d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('customerEmail', sa.String(length=256), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'customerEmail')
    # ### end Alembic commands ###
