import json
import pytest
from datetime import datetime, timedelta
from app.models import Titulo
from app import db

def test_get_titulos(client, init_database, auth_headers):
    """Testa a listagem de títulos"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/titulos/',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'titulos' in data
    assert len(data['titulos']) > 0
    assert 'total' in data
    assert data['total'] > 0

def test_get_titulos_with_filters(client, init_database, auth_headers):
    """Testa a listagem de títulos com filtros"""
    headers = auth_headers(1)
    
    # Teste com filtro de número
    response = client.get(
        '/api/titulos/?numero=12345',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['titulos']) > 0
    assert data['titulos'][0]['numero'] == '12345'
    
    # Teste com filtro de status
    response = client.get(
        '/api/titulos/?status=Pendente',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['titulos']) > 0
    assert data['titulos'][0]['status'] == 'Pendente'

def test_get_titulo_detail(client, init_database, auth_headers):
    """Testa a obtenção de detalhes de um título específico"""
    headers = auth_headers(1)
    
    # Obter o ID do título de teste
    titulo_id = init_database['titulo'].id
    
    response = client.get(
        f'/api/titulos/{titulo_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == titulo_id
    assert data['numero'] == '12345'
    assert data['protocolo'] == 'PROT12345'
    assert float(data['valor']) == 1000.50

def test_get_nonexistent_titulo(client, auth_headers):
    """Testa a obtenção de um título que não existe"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/titulos/9999',  # ID que não existe
        headers=headers
    )
    
    assert response.status_code == 404

def test_create_titulo(client, init_database, auth_headers):
    """Testa a criação de um novo título"""
    headers = auth_headers(1)
    
    new_titulo_data = {
        'numero': '54321',
        'protocolo': 'PROT54321',
        'valor': 2000.75,
        'data_emissao': '2023-03-01',
        'data_vencimento': '2023-04-01',
        'status': 'Pendente',
        'remessa_id': init_database['remessa'].id,
        'credor_id': init_database['credor'].id,
        'devedor_id': init_database['devedor'].id,
        'especie': 'DMI',
        'aceite': True,
        'nosso_numero': '98765'
    }
    
    response = client.post(
        '/api/titulos/',
        data=json.dumps(new_titulo_data),
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['numero'] == '54321'
    assert data['protocolo'] == 'PROT54321'
    assert float(data['valor']) == 2000.75
    
    # Verificar se o título foi realmente criado no banco
    titulo = Titulo.query.filter_by(protocolo='PROT54321').first()
    assert titulo is not None
    assert titulo.numero == '54321'

def test_update_titulo(client, init_database, auth_headers):
    """Testa a atualização de um título existente"""
    headers = auth_headers(1)
    
    # Obter o ID do título de teste
    titulo_id = init_database['titulo'].id
    
    update_data = {
        'status': 'Protestado',
        'data_protesto': datetime.now().strftime('%Y-%m-%d')
    }
    
    response = client.put(
        f'/api/titulos/{titulo_id}',
        data=json.dumps(update_data),
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'Protestado'
    assert data['data_protesto'] is not None
    
    # Verificar se o título foi realmente atualizado no banco
    titulo = Titulo.query.get(titulo_id)
    assert titulo.status == 'Protestado'

def test_delete_titulo(client, init_database, auth_headers):
    """Testa a exclusão de um título"""
    headers = auth_headers(1)
    
    # Criar um título específico para exclusão
    titulo_to_delete = Titulo(
        numero='99999',
        protocolo='DELETE99999',
        valor=500.00,
        data_emissao='2023-05-01',
        data_vencimento='2023-06-01',
        status='Pendente',
        remessa_id=init_database['remessa'].id,
        credor_id=init_database['credor'].id,
        devedor_id=init_database['devedor'].id,
        especie='DMI',
        aceite=False,
        nosso_numero='11111'
    )
    db.session.add(titulo_to_delete)
    db.session.commit()
    
    titulo_id = titulo_to_delete.id
    
    response = client.delete(
        f'/api/titulos/{titulo_id}',
        headers=headers
    )
    
    assert response.status_code == 204
    
    # Verificar se o título foi realmente excluído
    titulo = Titulo.query.get(titulo_id)
    assert titulo is None