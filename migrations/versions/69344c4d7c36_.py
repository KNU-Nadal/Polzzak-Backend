"""empty message

Revision ID: 69344c4d7c36
Revises: 638a6f15bd29
Create Date: 2024-09-19 02:02:33.376734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69344c4d7c36'
down_revision = '638a6f15bd29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('place', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=150), nullable=False))
        batch_op.create_unique_constraint(batch_op.f('uq_place_address'), ['address'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('place', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_place_address'), type_='unique')
        batch_op.drop_column('address')

    # ### end Alembic commands ###
