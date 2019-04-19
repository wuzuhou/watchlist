"""empty message

Revision ID: 814d5c23d6fa
Revises: 28d55a33be51
Create Date: 2019-04-19 11:18:09.985924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '814d5c23d6fa'
down_revision = '28d55a33be51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('sn_of_message', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'sn_of_message')
    # ### end Alembic commands ###