import json
import pytest
from app.models import User
from app import db

def test_login_success(client, init_database):
    """Testa login com credenciais válidas"""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_invalid_credentials(client, init_database):
    """Testa login com credenciais inválidas"""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'senha_errada'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert 'message' in data
    assert 'Credenciais inválidas' in data['message']

def test_login_missing_fields(client):
    """Testa login com campos faltando"""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com'
            # Falta o campo password
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'message' in data
    assert 'Dados incompletos' in data['message']

def test_get_user_info(client, init_database, auth_headers):
    """Testa obtenção de informações do usuário autenticado"""
    headers = auth_headers(1)  # ID do usuário de teste
    
    response = client.get(
        '/api/auth/me',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['email'] == 'test@example.com'
    assert data['username'] == 'testuser'
    assert data['nome_completo'] == 'Usuário de Teste'

def test_get_user_info_unauthorized(client):
    """Testa acesso não autorizado às informações do usuário"""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401

def test_user_inactive(client, init_database):
    """Testa login com usuário inativo"""
    # Desativar o usuário de teste
    user = User.query.filter_by(email='test@example.com').first()
    user.ativo = False
    db.session.commit()
    
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 403
    assert 'Usuário desativado' in data['message']
    
    # Reativar o usuário para outros testes
    user.ativo = True
    db.session.commit()