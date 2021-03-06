"""empty message

Revision ID: b6f422494ff2
Revises: 3a68082c83cb
Create Date: 2020-05-01 00:05:43.263236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6f422494ff2'
down_revision = '3a68082c83cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('state', sa.String(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('booking', 'state')
    # ### end Alembic commands ###
