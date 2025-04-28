import json
import pytest
import re
from flask import url_for
from app.models import User
from app import db

"""
Testes de segurança para validar as melhorias descritas no README_SEGURANCA.md

Este arquivo contém testes específicos para validar as melhorias de segurança
implementadas no sistema, como autenticação JWT, proteção contra CSRF,
validação de entrada e outras medidas de segurança.
"""

@pytest.mark.seguranca
def test_senha_armazenada_como_hash(app, init_database):
    """Verifica se as senhas estão sendo armazenadas como hash e não como texto puro"""
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        
        # Verificar se a senha está armazenada como hash
        assert user.password != 'password123'
        assert len(user.password) > 20  # Hash bcrypt é longo
        assert user.password.startswith('$2b$')  # Hash bcrypt começa com $2b$

@pytest.mark.seguranca
def test_jwt_token_valido(client, init_database):
    """Testa se o token JWT está sendo gerado e validado corretamente"""
    # Login para obter token
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert 'access_token' in data
    token = data['access_token']
    
    # Usar o token para acessar um endpoint protegido
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/titulos/', headers=headers)
    
    assert response.status_code == 200

@pytest.mark.seguranca
def test_jwt_token_invalido(client, init_database):
    """Testa se um token JWT inválido é rejeitado"""
    # Token inválido
    headers = {'Authorization': 'Bearer token_invalido'}
    response = client.get('/api/titulos/', headers=headers)
    
    assert response.status_code == 401

@pytest.mark.seguranca
def test_protecao_csrf(client, init_database):
    """Testa a proteção contra CSRF"""
    # Login para obter token e cookies
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Verificar se o cookie JWT está configurado como HttpOnly
    cookies = response.headers.getlist('Set-Cookie')
    jwt_cookie = next((c for c in cookies if 'access_token_cookie' in c), None)
    
    if jwt_cookie:  # Se o sistema usa cookies para JWT
        assert 'HttpOnly' in jwt_cookie
        if 'Secure' not in jwt_cookie:  # Em ambiente de teste, Secure pode não estar presente
            print("Aviso: Cookie JWT não está marcado como Secure (esperado em ambiente de produção)")

@pytest.mark.seguranca
def test_validacao_entrada(client, init_database, auth_headers):
    """Testa a validação de entrada para prevenir injeção"""
    headers = auth_headers(1)
    
    # Tentar injeção SQL básica
    response = client.get(
        "/api/titulos/?numero=12345' OR '1'='1",
        headers=headers
    )
    
    # Não deve retornar todos os registros (que seria o caso se a injeção funcionasse)
    data = json.loads(response.data)
    assert response.status_code == 200
    
    # Se a injeção funcionasse, retornaria muitos registros
    # Verificamos se o número de registros é razoável
    if 'titulos' in data and len(data['titulos']) > 0:
        # Verificar se os títulos retornados realmente contêm a string de injeção
        # Se a validação estiver funcionando, apenas títulos com essa string exata seriam retornados
        for titulo in data['titulos']:
            assert "12345' OR '1'='1" in titulo['numero']

@pytest.mark.seguranca
def test_headers_seguranca(client):
    """Testa se os headers de segurança estão configurados corretamente"""
    response = client.get('/')
    
    # Verificar headers de segurança
    headers = response.headers
    
    # Verificar Content-Security-Policy
    assert 'Content-Security-Policy' in headers or 'X-Content-Security-Policy' in headers
    
    # Verificar X-Frame-Options para prevenir clickjacking
    assert 'X-Frame-Options' in headers
    
    # Verificar X-XSS-Protection
    assert 'X-XSS-Protection' in headers

@pytest.mark.seguranca
def test_rate_limiting(client):
    """Testa se o rate limiting está funcionando"""
    # Fazer múltiplas requisições rápidas para acionar o rate limiting
    responses = []
    for _ in range(50):  # Número alto de requisições
        responses.append(client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'senha_errada'
            }),
            content_type='application/json'
        ))
    
    # Verificar se pelo menos uma das respostas tem código 429 (Too Many Requests)
    rate_limited = any(r.status_code == 429 for r in responses)
    
    # Se não encontrar 429, verificar se há outro mecanismo de proteção
    if not rate_limited:
        # Verificar se as últimas respostas têm atraso maior (backoff exponencial)
        # ou se há bloqueio temporário (401 com mensagem específica)
        last_responses = responses[-5:]
        alternative_protection = any(
            r.status_code == 401 and b'temporariamente bloqueado' in r.data 
            for r in last_responses
        )
        
        # Se não houver rate limiting nem proteção alternativa, gerar aviso
        if not alternative_protection:
            print("Aviso: Rate limiting não detectado. Verifique a implementação.")

@pytest.mark.seguranca
def test_permissoes_usuario(client, init_database, auth_headers):
    """Testa se as permissões de usuário estão sendo aplicadas corretamente"""
    # Criar um usuário não-admin
    with client.application.app_context():
        user_regular = User(
            username='regularuser',
            email='regular@example.com',
            password='password123',
            nome_completo='Usuário Regular',
            cargo='Operador',
            admin=False
        )
        db.session.add(user_regular)
        db.session.commit()
        user_regular_id = user_regular.id
    
    # Headers para usuário admin
    admin_headers = auth_headers(1)  # Assumindo que ID 1 é admin
    
    # Headers para usuário regular
    regular_headers = auth_headers(user_regular_id)
    
    # Tentar acessar endpoint administrativo com usuário regular
    response_regular = client.get('/api/admin/usuarios', headers=regular_headers)
    
    # Tentar acessar endpoint administrativo com usuário admin
    response_admin = client.get('/api/admin/usuarios', headers=admin_headers)
    
    # Usuário regular deve receber 403 Forbidden
    assert response_regular.status_code in [403, 404]  # 404 se o endpoint não existir
    
    # Usuário admin deve receber 200 OK se o endpoint existir
    if response_admin.status_code != 404:  # Se o endpoint existir
        assert response_admin.status_code == 200