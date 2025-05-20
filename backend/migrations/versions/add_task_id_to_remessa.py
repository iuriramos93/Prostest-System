"""add task_id to remessa

Revision ID: 7a9b5e31f254
Revises: 49ab0e31e253
Create Date: 2025-05-20 00:08:10.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a9b5e31f254'
down_revision = '49ab0e31e253'
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona a coluna task_id à tabela remessas
    op.add_column('remessas', sa.Column('task_id', sa.String(50), nullable=True))


def downgrade():
    # Remove a coluna task_id da tabela remessas
    op.drop_column('remessas', 'task_id')
