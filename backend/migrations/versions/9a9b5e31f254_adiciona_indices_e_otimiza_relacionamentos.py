"""Adiciona índices e otimiza relacionamentos

Revision ID: 9a9b5e31f254
Revises: 8a9b5e31f254
Create Date: 2025-05-22 02:00:30.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a9b5e31f254'
down_revision = '8a9b5e31f254'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar índices compostos para melhorar performance de consultas frequentes
    op.create_index('idx_titulos_status_data', 'titulos', ['status', 'data_vencimento'], unique=False)
    op.create_index('idx_remessas_status_data', 'remessas', ['status', 'data_envio'], unique=False)
    op.create_index('idx_desistencias_status_data', 'desistencias', ['status', 'data_solicitacao'], unique=False)
    
    # Adicionar índice para busca de usuários por nome
    op.create_index('idx_users_nome', 'users', ['nome_completo'], unique=False)


def downgrade():
    # Remover índices adicionados
    op.drop_index('idx_titulos_status_data', table_name='titulos')
    op.drop_index('idx_remessas_status_data', table_name='remessas')
    op.drop_index('idx_desistencias_status_data', table_name='desistencias')
    op.drop_index('idx_users_nome', table_name='users')
