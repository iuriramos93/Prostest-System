"""Atualiza configuração do Flask-Limiter para usar Redis

Revision ID: 8a9b5e31f254
Revises: 7a9b5e31f254
Create Date: 2025-05-22 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a9b5e31f254'
down_revision = '7a9b5e31f254'
branch_labels = None
depends_on = None


def upgrade():
    # Este é um arquivo de migração vazio, pois a alteração é apenas na configuração
    # do Flask-Limiter e não no schema do banco de dados
    pass


def downgrade():
    # Como não há alterações no schema, não há nada para reverter
    pass
