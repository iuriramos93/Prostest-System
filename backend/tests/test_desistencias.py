import json
import pytest
from datetime import datetime
from app.models import Desistencia
from app import db

def test_get_desistencias(client, init_database, auth_headers):
    """Testa a listagem de desistências"""
    headers = auth_headers(1)
    
    # Criar algumas desistências para testar
    desistencia1 = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Pagamento realizado',
        observacoes='Teste de desistência 1',
        status='Pendente',
        usuario_id=1
    )
    
    desistencia2 = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Acordo entre as partes',
        observacoes='Teste de desistência 2',
        status='Aprovada',
        usuario_id=1,
        data_processamento=datetime.utcnow(),
        usuario_processamento_id=1
    )
    
    db.session.add_all([desistencia1, desistencia2])
    db.session.commit()
    
    response = client.get(
        '/api/desistencias/',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'desistencias' in data
    assert len(data['desistencias']) >= 2
    assert 'total' in data
    assert data['total'] >= 2

def test_get_desistencias_with_filters(client, init_database, auth_headers):
    """Testa a listagem de desistências com filtros"""
    headers = auth_headers(1)
    
    # Teste com filtro de status
    response = client.get(
        '/api/desistencias/?status=Pendente',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['desistencias']) > 0
    for desistencia in data['desistencias']:
        assert desistencia['status'] == 'Pendente'
    
    # Teste com filtro de título_id
    titulo_id = init_database['titulo'].id
    response = client.get(
        f'/api/desistencias/?titulo_id={titulo_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['desistencias']) > 0
    for desistencia in data['desistencias']:
        assert desistencia['titulo_id'] == titulo_id

def test_get_desistencia_detail(client, init_database, auth_headers):
    """Testa a obtenção de detalhes de uma desistência específica"""
    headers = auth_headers(1)
    
    # Criar uma desistência para testar
    desistencia = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Motivo para teste de detalhes',
        observacoes='Teste de detalhes',
        status='Pendente',
        usuario_id=1
    )
    db.session.add(desistencia)
    db.session.commit()
    
    desistencia_id = desistencia.id
    
    response = client.get(
        f'/api/desistencias/{desistencia_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == desistencia_id
    assert data['motivo'] == 'Motivo para teste de detalhes'
    assert data['observacoes'] == 'Teste de detalhes'
    assert data['status'] == 'Pendente'

def test_get_nonexistent_desistencia(client, auth_headers):
    """Testa a obtenção de uma desistência que não existe"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/desistencias/9999',  # ID que não existe
        headers=headers
    )
    
    assert response.status_code == 404

def test_create_desistencia(client, init_database, auth_headers):
    """Testa a criação de uma nova desistência"""
    headers = auth_headers(1)
    
    new_desistencia_data = {
        'titulo_id': init_database['titulo'].id,
        'motivo': 'Novo motivo de teste',
        'observacoes': 'Observações para nova desistência'
    }
    
    response = client.post(
        '/api/desistencias/',
        data=json.dumps(new_desistencia_data),
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['titulo_id'] == init_database['titulo'].id
    assert data['motivo'] == 'Novo motivo de teste'
    assert data['observacoes'] == 'Observações para nova desistência'
    assert data['status'] == 'Pendente'  # Status inicial deve ser Pendente
    
    # Verificar se a desistência foi realmente criada no banco
    desistencia = Desistencia.query.get(data['id'])
    assert desistencia is not None
    assert desistencia.motivo == 'Novo motivo de teste'

def test_aprovar_desistencia(client, init_database, auth_headers):
    """Testa a aprovação de uma desistência"""
    headers = auth_headers(1)
    
    # Criar uma desistência pendente para aprovar
    desistencia = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Motivo para aprovação',
        observacoes='Teste de aprovação',
        status='Pendente',
        usuario_id=1
    )
    db.session.add(desistencia)
    db.session.commit()
    
    desistencia_id = desistencia.id
    
    response = client.post(
        f'/api/desistencias/{desistencia_id}/aprovar',
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == desistencia_id
    assert data['status'] == 'Aprovada'
    assert data['data_processamento'] is not None
    assert data['usuario_processamento_id'] == 1
    
    # Verificar se a desistência foi realmente aprovada no banco
    desistencia = Desistencia.query.get(desistencia_id)
    assert desistencia.status == 'Aprovada'
    assert desistencia.data_processamento is not None

def test_rejeitar_desistencia(client, init_database, auth_headers):
    """Testa a rejeição de uma desistência"""
    headers = auth_headers(1)
    
    # Criar uma desistência pendente para rejeitar
    desistencia = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Motivo para rejeição',
        observacoes='Teste de rejeição',
        status='Pendente',
        usuario_id=1
    )
    db.session.add(desistencia)
    db.session.commit()
    
    desistencia_id = desistencia.id
    
    rejeicao_data = {
        'motivo_rejeicao': 'Documentação incompleta'
    }
    
    response = client.post(
        f'/api/desistencias/{desistencia_id}/rejeitar',
        data=json.dumps(rejeicao_data),
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == desistencia_id
    assert data['status'] == 'Rejeitada'
    assert data['motivo_rejeicao'] == 'Documentação incompleta'
    assert data['data_processamento'] is not None
    assert data['usuario_processamento_id'] == 1
    
    # Verificar se a desistência foi realmente rejeitada no banco
    desistencia = Desistencia.query.get(desistencia_id)
    assert desistencia.status == 'Rejeitada'
    assert desistencia.motivo_rejeicao == 'Documentação incompleta'
    assert desistencia.data_processamento is not None