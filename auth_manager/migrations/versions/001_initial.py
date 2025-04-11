"""Initial migration for carrier tokens

Revision ID: 001
Revises: 
Create Date: 2024-04-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'carrier_tokens',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), index=True),
        sa.Column('carrier', sa.String(), index=True),
        sa.Column('access_token', sa.String()),
        sa.Column('refresh_token', sa.String()),
        sa.Column('token_type', sa.String()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('scope', sa.String(), nullable=True),
        sa.Column('additional_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )

def downgrade():
    op.drop_table('carrier_tokens') 