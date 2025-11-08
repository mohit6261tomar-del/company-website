"""Add new columns to service table

Revision ID: 8f7a6e5d4c3b
Revises: e5e3fe1f1ec4
Create Date: 2025-10-07 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '8f7a6e5d4c3b'
down_revision = 'e5e3fe1f1ec4'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to service table
    op.add_column('service', sa.Column('slug', sa.String(length=100), nullable=False, server_default=''))
    op.add_column('service', sa.Column('content', sa.Text(), nullable=True))
    op.add_column('service', sa.Column('image_path', sa.String(length=200), nullable=True))
    op.add_column('service', sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('service', sa.Column('order_position', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('service', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Create index on slug
    op.create_index(op.f('ix_service_slug'), 'service', ['slug'], unique=True)
    
    # Set default values for existing rows
    op.execute("""
        UPDATE service 
        SET 
            slug = LOWER(REPLACE(title, ' ', '-')),
            content = description,
            is_featured = 0,
            order_position = id,
            updated_at = CURRENT_TIMESTAMP
        WHERE slug IS NULL;
    """)
    
    # Make slug non-nullable after setting default values
    with op.batch_alter_table('service') as batch_op:
        batch_op.alter_column('slug', nullable=False)

def downgrade():
    # Drop the index first
    op.drop_index(op.f('ix_service_slug'), table_name='service')
    
    # Drop the columns
    with op.batch_alter_table('service') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('order_position')
        batch_op.drop_column('is_featured')
        batch_op.drop_column('image_path')
        batch_op.drop_column('content')
        batch_op.drop_column('slug')
