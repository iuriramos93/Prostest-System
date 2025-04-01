import json
import pytest
import io
from app.models import Remessa
from app import db

def test_get_remessas(client, init_database, auth_headers):
    """Testa a listagem de remessas"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/remessas/',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'remessas' in data
    assert len(data['remessas']) > 0
    assert 'total' in data
    assert data['total'] > 0

def test_get_remessas_with_filters(client, init_database, auth_headers):
    """Testa a listagem de remessas com filtros"""
    headers = auth_headers(1)
    
    # Teste com filtro de status
    response = client.get(
        '/api/remessas/?status=Processado',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['remessas']) > 0
    assert data['remessas'][0]['status'] == 'Processado'
    
    # Teste com filtro de UF
    response = client.get(
        '/api/remessas/?uf=SP',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['remessas']) > 0
    assert data['remessas'][0]['uf'] == 'SP'

def test_get_remessa_detail(client, init_database, auth_headers):
    """Testa a obtenção de detalhes de uma remessa específica"""
    headers = auth_headers(1)
    
    # Obter o ID da remessa de teste
    remessa_id = init_database['remessa'].id
    
    response = client.get(
        f'/api/remessas/{remessa_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == remessa_id
    assert data['nome_arquivo'] == 'remessa_teste.txt'
    assert data['status'] == 'Processado'
    assert data['uf'] == 'SP'

def test_get_nonexistent_remessa(client, auth_headers):
    """Testa a obtenção de uma remessa que não existe"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/remessas/9999',  # ID que não existe
        headers=headers
    )
    
    assert response.status_code == 404

def test_upload_remessa(client, init_database, auth_headers):
    """Testa o upload de uma nova remessa"""
    headers = auth_headers(1)
    # Remover o header Authorization para enviar no form data
    auth_token = headers['Authorization']
    
    # Criar um arquivo de teste
    file_content = b"Conteudo de teste da remessa"
    data = {
        'arquivo': (io.BytesIO(file_content), 'nova_remessa.txt'),
        'uf': 'RJ',
        'tipo': 'Remessa'
    }
    
    response = client.post(
        '/api/remessas/upload',
        data=data,
        headers={'Authorization': auth_token},
        content_type='multipart/form-data'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'id' in data
    assert data['nome_arquivo'] == 'nova_remessa.txt'
    assert data['status'] == 'Pendente'  # Status inicial deve ser Pendente
    assert data['uf'] == 'RJ'
    
    # Verificar se a remessa foi realmente criada no banco
    remessa = Remessa.query.filter_by(nome_arquivo='nova_remessa.txt').first()
    assert remessa is not None
    assert remessa.uf == 'RJ'

def test_process_remessa(client, init_database, auth_headers):
    """Testa o processamento de uma remessa"""
    headers = auth_headers(1)
    
    # Criar uma remessa pendente para processamento
    remessa_pendente = Remessa(
        nome_arquivo='remessa_pendente.txt',
        status='Pendente',
        uf='MG',
        tipo='Remessa',
        quantidade_titulos=0,
        usuario_id=1
    )
    db.session.add(remessa_pendente)
    db.session.commit()
    
    remessa_id = remessa_pendente.id
    
    response = client.post(
        f'/api/remessas/{remessa_id}/processar',
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == remessa_id
    assert data['status'] == 'Processado'  # Status deve ser atualizado para Processado
    
    # Verificar se a remessa foi realmente processada no banco
    remessa = Remessa.query.get(remessa_id)
    assert remessa.status == 'Processado'
    assert remessa.data_processamento is not None

def test_delete_remessa(client, init_database, auth_headers):
    """Testa a exclusão de uma remessa"""
    headers = auth_headers(1)
    
    # Criar uma remessa específica para exclusão
    remessa_to_delete = Remessa(
        nome_arquivo='remessa_to_delete.txt',
        status='Processado',
        uf='SC',
        tipo='Remessa',
        quantidade_titulos=0,
        usuario_id=1
    )
    db.session.add(remessa_to_delete)
    db.session.commit()
    
    remessa_id = remessa_to_delete.id
    
    response = client.delete(
        f'/api/remessas/{remessa_id}',
        headers=headers
    )
    
    assert response.status_code == 204
    
    # Verificar se a remessa foi realmente excluída
    remessa = Remessa.query.get(remessa_id)
    assert remessa is None