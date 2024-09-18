"""empty message

Revision ID: 638a6f15bd29
Revises: 
Create Date: 2024-09-18 15:36:18.892390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '638a6f15bd29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('place',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_place')),
    sa.UniqueConstraint('name', name=op.f('uq_place_name'))
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kakao_id', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('profile_image', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('kakao_id', name=op.f('uq_user_kakao_id'))
    )
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('place_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['place_id'], ['place.id'], name=op.f('fk_event_place_id_place'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_event')),
    sa.UniqueConstraint('title', name=op.f('uq_event_title'))
    )
    op.create_table('market',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['place_id'], ['place.id'], name=op.f('fk_market_place_id_place'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_market'))
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['place_id'], ['place.id'], name=op.f('fk_review_place_id_place'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_review_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_review'))
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=False),
    sa.Column('place_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['user.id'], name=op.f('fk_team_admin_id_user'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['place_id'], ['place.id'], name=op.f('fk_team_place_id_place'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_team')),
    sa.UniqueConstraint('title', name=op.f('uq_team_title'))
    )
    op.create_table('user_event',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name=op.f('fk_user_event_event_id_event'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_event_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'event_id', name=op.f('pk_user_event'))
    )
    op.create_table('user_team',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], name=op.f('fk_user_team_team_id_team'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_team_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'team_id', name=op.f('pk_user_team'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_team')
    op.drop_table('user_event')
    op.drop_table('team')
    op.drop_table('review')
    op.drop_table('market')
    op.drop_table('event')
    op.drop_table('user')
    op.drop_table('place')
    # ### end Alembic commands ###