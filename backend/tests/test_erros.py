import json
import pytest
from app.models import Erro
from app import db

def test_get_erros(client, init_database, auth_headers):
    """Testa a listagem de erros"""
    headers = auth_headers(1)
    
    # Criar alguns erros para testar
    erro1 = Erro(
        remessa_id=init_database['remessa'].id,
        titulo_id=init_database['titulo'].id,
        codigo='E001',
        descricao='Erro de teste 1',
        linha=10,
        status='Pendente'
    )
    
    erro2 = Erro(
        remessa_id=init_database['remessa'].id,
        codigo='E002',
        descricao='Erro de teste 2',
        linha=20,
        status='Resolvido'
    )
    
    db.session.add_all([erro1, erro2])
    db.session.commit()
    
    response = client.get(
        '/api/erros/',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'erros' in data
    assert len(data['erros']) >= 2
    assert 'total' in data
    assert data['total'] >= 2

def test_get_erros_with_filters(client, init_database, auth_headers):
    """Testa a listagem de erros com filtros"""
    headers = auth_headers(1)
    
    # Teste com filtro de status
    response = client.get(
        '/api/erros/?status=Pendente',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['erros']) > 0
    for erro in data['erros']:
        assert erro['status'] == 'Pendente'
    
    # Teste com filtro de remessa_id
    remessa_id = init_database['remessa'].id
    response = client.get(
        f'/api/erros/?remessa_id={remessa_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['erros']) > 0
    for erro in data['erros']:
        assert erro['remessa_id'] == remessa_id

def test_get_erro_detail(client, init_database, auth_headers):
    """Testa a obtenção de detalhes de um erro específico"""
    headers = auth_headers(1)
    
    # Criar um erro para testar
    erro = Erro(
        remessa_id=init_database['remessa'].id,
        titulo_id=init_database['titulo'].id,
        codigo='E003',
        descricao='Erro de teste para detalhes',
        linha=30,
        status='Pendente'
    )
    db.session.add(erro)
    db.session.commit()
    
    erro_id = erro.id
    
    response = client.get(
        f'/api/erros/{erro_id}',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == erro_id
    assert data['codigo'] == 'E003'
    assert data['descricao'] == 'Erro de teste para detalhes'
    assert data['linha'] == 30
    assert data['status'] == 'Pendente'

def test_get_nonexistent_erro(client, auth_headers):
    """Testa a obtenção de um erro que não existe"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/erros/9999',  # ID que não existe
        headers=headers
    )
    
    assert response.status_code == 404

def test_update_erro_status(client, init_database, auth_headers):
    """Testa a atualização do status de um erro"""
    headers = auth_headers(1)
    
    # Criar um erro para testar
    erro = Erro(
        remessa_id=init_database['remessa'].id,
        codigo='E004',
        descricao='Erro de teste para atualização',
        linha=40,
        status='Pendente'
    )
    db.session.add(erro)
    db.session.commit()
    
    erro_id = erro.id
    
    update_data = {
        'status': 'Resolvido',
        'observacao': 'Erro corrigido durante teste'
    }
    
    response = client.put(
        f'/api/erros/{erro_id}',
        data=json.dumps(update_data),
        headers=headers,
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == erro_id
    assert data['status'] == 'Resolvido'
    assert data['observacao'] == 'Erro corrigido durante teste'
    
    # Verificar se o erro foi realmente atualizado no banco
    erro = Erro.query.get(erro_id)
    assert erro.status == 'Resolvido'
    assert erro.observacao == 'Erro corrigido durante teste'

def test_analise_erros(client, init_database, auth_headers):
    """Testa a análise de erros por tipo"""
    headers = auth_headers(1)
    
    # Criar vários erros com códigos diferentes para testar a análise
    erros = [
        Erro(remessa_id=init_database['remessa'].id, codigo='E001', descricao='Erro tipo 1', linha=1, status='Pendente'),
        Erro(remessa_id=init_database['remessa'].id, codigo='E001', descricao='Erro tipo 1', linha=2, status='Pendente'),
        Erro(remessa_id=init_database['remessa'].id, codigo='E002', descricao='Erro tipo 2', linha=3, status='Pendente'),
        Erro(remessa_id=init_database['remessa'].id, codigo='E003', descricao='Erro tipo 3', linha=4, status='Resolvido'),
        Erro(remessa_id=init_database['remessa'].id, codigo='E003', descricao='Erro tipo 3', linha=5, status='Resolvido')
    ]
    db.session.add_all(erros)
    db.session.commit()
    
    response = client.get(
        '/api/erros/analise',
        headers=headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'analise' in data
    assert len(data['analise']) > 0
    
    # Verificar se a análise contém os códigos de erro esperados
    codigos_erro = [item['codigo'] for item in data['analise']]
    assert 'E001' in codigos_erro
    assert 'E002' in codigos_erro
    assert 'E003' in codigos_erro
    
    # Verificar se as contagens estão corretas
    for item in data['analise']:
        if item['codigo'] == 'E001':
            assert item['count'] >= 2
        elif item['codigo'] == 'E002':
            assert item['count'] >= 1
        elif item['codigo'] == 'E003':
            assert item['count'] >= 2