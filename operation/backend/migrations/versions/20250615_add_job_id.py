"""add job_id to product_descriptions and generated_images

Revision ID: 20250615_add_job_id
Revises: 4ece42cf2d1d
Create Date: 2025-06-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250615_add_job_id'
down_revision: Union[str, None] = '4ece42cf2d1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add job_id column to product_descriptions table
    op.add_column('product_descriptions', sa.Column('job_id', sa.String(36), nullable=True))
    op.create_index('ix_product_descriptions_job_id', 'product_descriptions', ['job_id'], unique=False)
    
    # Add job_id column to generated_images table
    op.add_column('generated_images', sa.Column('job_id', sa.String(36), nullable=True))
    op.create_index('ix_generated_images_job_id', 'generated_images', ['job_id'], unique=False)


def downgrade() -> None:
    # Remove job_id column from generated_images table
    op.drop_index('ix_generated_images_job_id', table_name='generated_images')
    op.drop_column('generated_images', 'job_id')
    
    # Remove job_id column from product_descriptions table
    op.drop_index('ix_product_descriptions_job_id', table_name='product_descriptions')
    op.drop_column('product_descriptions', 'job_id')
