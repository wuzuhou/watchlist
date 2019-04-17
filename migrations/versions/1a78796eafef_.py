"""empty message

Revision ID: 1a78796eafef
Revises: 2141a5c14ac6
Create Date: 2019-04-16 19:00:20.211680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a78796eafef'
down_revision = '2141a5c14ac6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('nickname', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'nickname')
    # ### end Alembic commands ###