"""empty message

Revision ID: 79e7c6442e7a
Revises: 814d5c23d6fa
Create Date: 2019-04-24 18:02:31.734995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79e7c6442e7a'
down_revision = '814d5c23d6fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'sn_of_message')
    op.add_column('movie', sa.Column('user_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movie', 'user_id')
    op.add_column('message', sa.Column('sn_of_message', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###