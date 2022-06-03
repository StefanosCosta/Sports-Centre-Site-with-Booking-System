"""empty message

Revision ID: 00325de0b951
Revises: 5bcce2be84af
Create Date: 2020-03-16 19:29:32.729841

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00325de0b951'
down_revision = '5bcce2be84af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles_users',
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], [u'role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], )
    )
    # ### end Alembic commands ###
