"""migrate

Revision ID: 70858f3f710a
Revises: 
Create Date: 2020-01-27 23:20:15.559929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70858f3f710a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('servicelocation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('language_code', sa.String(length=2), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('country_code')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_ko', sa.String(length=15), nullable=False),
    sa.Column('tag_jp', sa.String(length=15), nullable=False),
    sa.Column('tag_en', sa.String(length=15), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag_en'),
    sa.UniqueConstraint('tag_jp'),
    sa.UniqueConstraint('tag_ko')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('represent_company_name', sa.String(length=50), nullable=False),
    sa.Column('for_service_location', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['for_service_location'], ['servicelocation.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id')
    )
    op.create_table('localization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(length=2), nullable=False),
    sa.Column('localization_company_name', sa.String(length=50), nullable=False),
    sa.Column('for_company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['for_company_id'], ['company.company_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('locsertagmapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('for_company_id', sa.Integer(), nullable=True),
    sa.Column('for_tag_id', sa.Integer(), nullable=True),
    sa.Column('for_service_location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['for_company_id'], ['company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['for_service_location_id'], ['servicelocation.id'], ),
    sa.ForeignKeyConstraint(['for_tag_id'], ['tag.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('locsertagmapping')
    op.drop_table('localization')
    op.drop_table('company')
    op.drop_table('tag')
    op.drop_table('servicelocation')
    # ### end Alembic commands ###