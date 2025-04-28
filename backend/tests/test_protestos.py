import json
import pytest
from datetime import datetime, timedelta
from app.models import Titulo, Devedor, Credor
from app import db

@pytest.mark.protestos
@pytest.mark.integration
def test_get_protestos(client, init_database, auth_headers):
    """Testa a listagem de protestos"""
    headers = auth_headers(1)
    
    # Criar um título protestado para o teste
    with client.application.app_context():
        titulo = Titulo.query.first()
        titulo.status = 'Protestado'
        titulo.data_protesto = datetime.now().date()
        db.session.commit()
    
    response = client.get(
        '/api/protestos/',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'items' in data
    assert len(data['items']) > 0
    assert 'total' in data
    assert data['total'] > 0

@pytest.mark.protestos
@pytest.mark.integration
def test_get_protestos_with_filters(client, init_database, auth_headers):
    """Testa a listagem de protestos com filtros"""
    headers = auth_headers(1)
    
    # Criar um título protestado para o teste
    with client.application.app_context():
        titulo = Titulo.query.first()
        titulo.status = 'Protestado'
        titulo.data_protesto = datetime.now().date()
        titulo.numero = '12345-PROTESTO'
        db.session.commit()
    
    # Teste com filtro de número
    response = client.get(
        '/api/protestos/?numero_titulo=12345',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['items']) > 0
    
    # Teste com filtro de data
    hoje = datetime.now().date().isoformat()
    response = client.get(
        f'/api/protestos/?data_inicio={hoje}&data_fim={hoje}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['items']) > 0

@pytest.mark.protestos
@pytest.mark.integration
def test_get_protesto_by_id(client, init_database, auth_headers):
    """Testa a obtenção de um protesto específico por ID"""
    headers = auth_headers(1)
    
    # Criar um título protestado para o teste
    with client.application.app_context():
        titulo = Titulo.query.first()
        titulo.status = 'Protestado'
        titulo.data_protesto = datetime.now().date()
        db.session.commit()
        titulo_id = titulo.id
    
    response = client.get(
        f'/api/protestos/{titulo_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == titulo_id
    assert data['status'] == 'Protestado'

@pytest.mark.protestos
@pytest.mark.integration
def test_get_protesto_not_found(client, init_database, auth_headers):
    """Testa a obtenção de um protesto inexistente"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/protestos/99999',  # ID inexistente
        headers=headers
    )
    
    assert response.status_code == 404

@pytest.mark.protestos
@pytest.mark.integration
def test_registrar_protesto(client, init_database, auth_headers):
    """Testa o registro de um protesto"""
    headers = auth_headers(1)
    
    # Obter um título não protestado
    with client.application.app_context():
        titulo = Titulo.query.filter_by(status='Pendente').first()
        if not titulo:
            # Criar um título pendente se não existir
            titulo = Titulo(
                numero='54321-PENDENTE',
                valor=500.00,
                data_emissao=datetime.now().date(),
                data_vencimento=(datetime.now() + timedelta(days=30)).date(),
                status='Pendente',
                credor_id=1,
                devedor_id=1,
                remessa_id=1
            )
            db.session.add(titulo)
            db.session.commit()
        
        titulo_id = titulo.id
    
    # Dados para registrar o protesto
    data = {
        'data_protesto': datetime.now().date().isoformat(),
        'valor_custas': 50.00,
        'observacao': 'Protesto registrado via teste automatizado'
    }
    
    response = client.post(
        f'/api/protestos/registrar',
        headers=headers,
        data=json.dumps({
            'titulo_id': titulo_id,
            **data
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verificar se o título foi atualizado
    with client.application.app_context():
        titulo_atualizado = Titulo.query.get(titulo_id)
        assert titulo_atualizado.status == 'Protestado'
        assert titulo_atualizado.data_protesto is not None

@pytest.mark.protestos
@pytest.mark.integration
def test_registrar_protesto_titulo_inexistente(client, init_database, auth_headers):
    """Testa o registro de protesto para um título inexistente"""
    headers = auth_headers(1)
    
    response = client.post(
        f'/api/protestos/registrar',
        headers=headers,
        data=json.dumps({
            'titulo_id': 99999,  # ID inexistente
            'data_protesto': datetime.now().date().isoformat(),
            'valor_custas': 50.00,
            'observacao': 'Teste com título inexistente'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 404

@pytest.mark.protestos
@pytest.mark.integration
def test_cancelar_protesto(client, init_database, auth_headers):
    """Testa o cancelamento de um protesto"""
    headers = auth_headers(1)
    
    # Criar um título protestado para o teste
    with client.application.app_context():
        titulo = Titulo.query.first()
        titulo.status = 'Protestado'
        titulo.data_protesto = datetime.now().date()
        db.session.commit()
        titulo_id = titulo.id
    
    response = client.post(
        f'/api/protestos/{titulo_id}/cancelar',
        headers=headers,
        data=json.dumps({
            'motivo': 'Cancelamento via teste automatizado',
            'data_cancelamento': datetime.now().date().isoformat()
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Verificar se o título foi atualizado
    with client.application.app_context():
        titulo_atualizado = Titulo.query.get(titulo_id)
        assert titulo_atualizado.status == 'Cancelado'
        assert titulo_atualizado.data_cancelamento is not None