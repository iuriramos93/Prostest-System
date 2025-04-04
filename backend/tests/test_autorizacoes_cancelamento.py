import os
import json
import pytest
from datetime import datetime, date
from io import BytesIO
from app.models import AutorizacaoCancelamento, TransacaoAutorizacaoCancelamento, Titulo


def test_upload_autorizacao_cancelamento(client, auth_headers, app):
    """Testa o upload de um arquivo de autorização de cancelamento"""
    # Criar um arquivo de teste
    content = (
        "0001BANCO TESTE                                  0102202300002                                                            00001\n"
        "1PROT12345010220231234567890DEVEDOR TESTE 1                         00000000010050A            67890           00002\n"
        "1PROT67890010220239876543210DEVEDOR TESTE 2                         00000000020075A            12345           00003\n"
        "9001BANCO TESTE                                  0102202300002                                                            00004"
    )
    data = {
        'file': (BytesIO(content.encode('latin-1')), 'AC001_01022023.txt')
    }
    
    # Fazer a requisição de upload
    response = client.post('/api/autorizacoes-cancelamento/upload', 
                          data=data,
                          headers=auth_headers())
    
    # Verificar se o upload foi bem-sucedido
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'autorizacao_id' in response_data
    
    # Verificar se o registro foi criado no banco de dados
    autorizacao_id = response_data['autorizacao_id']
    with app.app_context():
        autorizacao = AutorizacaoCancelamento.query.get(autorizacao_id)
        assert autorizacao is not None
        assert autorizacao.codigo_apresentante == '001'
        assert autorizacao.nome_apresentante == 'BANCO TESTE'
        assert autorizacao.data_movimento == date(2023, 2, 1)
        assert autorizacao.quantidade_solicitacoes == 2
        assert autorizacao.status == 'Processado'
        
        # Verificar se as transações foram criadas
        transacoes = TransacaoAutorizacaoCancelamento.query.filter_by(autorizacao_id=autorizacao_id).all()
        assert len(transacoes) == 2
        
        # Verificar dados da primeira transação
        assert transacoes[0].numero_protocolo == 'PROT12345'
        assert transacoes[0].data_protocolizacao == date(2023, 2, 1)
        assert transacoes[0].numero_titulo == '1234567890'
        assert transacoes[0].nome_devedor == 'DEVEDOR TESTE 1'
        assert float(transacoes[0].valor_titulo) == 100.50
        assert transacoes[0].solicitacao_cancelamento == 'A'
        assert transacoes[0].carteira_nosso_numero == '67890'


def test_listar_autorizacoes(client, auth_headers, app, init_database):
    """Testa a listagem de autorizações de cancelamento"""
    # Criar uma autorização de teste
    with app.app_context():
        autorizacao = AutorizacaoCancelamento(
            arquivo_nome='AC001_01022023.txt',
            codigo_apresentante='001',
            nome_apresentante='BANCO TESTE',
            data_movimento=date(2023, 2, 1),
            quantidade_solicitacoes=2,
            status='Processado',
            usuario_id=1
        )
        db = app.extensions['sqlalchemy'].db
        db.session.add(autorizacao)
        db.session.commit()
    
    # Fazer a requisição de listagem
    response = client.get('/api/autorizacoes-cancelamento/', headers=auth_headers())
    
    # Verificar se a listagem foi bem-sucedida
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'autorizacoes' in response_data
    assert len(response_data['autorizacoes']) >= 1
    
    # Verificar se a autorização criada está na lista
    found = False
    for a in response_data['autorizacoes']:
        if a['codigo_apresentante'] == '001' and a['nome_apresentante'] == 'BANCO TESTE':
            found = True
            break
    assert found


def test_detalhes_autorizacao(client, auth_headers, app, init_database):
    """Testa a obtenção de detalhes de uma autorização de cancelamento"""
    # Criar uma autorização de teste
    with app.app_context():
        autorizacao = AutorizacaoCancelamento(
            arquivo_nome='AC001_01022023.txt',
            codigo_apresentante='001',
            nome_apresentante='BANCO TESTE',
            data_movimento=date(2023, 2, 1),
            quantidade_solicitacoes=2,
            status='Processado',
            usuario_id=1
        )
        db = app.extensions['sqlalchemy'].db
        db.session.add(autorizacao)
        db.session.commit()
        autorizacao_id = autorizacao.id
    
    # Fazer a requisição de detalhes
    response = client.get(f'/api/autorizacoes-cancelamento/{autorizacao_id}', headers=auth_headers())
    
    # Verificar se a obtenção de detalhes foi bem-sucedida
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['codigo_apresentante'] == '001'
    assert response_data['nome_apresentante'] == 'BANCO TESTE'
    assert response_data['status'] == 'Processado'


def test_processar_transacao(client, auth_headers, app, init_database):
    """Testa o processamento de uma transação de autorização de cancelamento"""
    # Criar uma autorização e uma transação de teste
    with app.app_context():
        db = app.extensions['sqlalchemy'].db
        
        # Obter um título existente e marcar como protestado
        titulo = Titulo.query.first()
        titulo.status = 'Protestado'
        titulo.protocolo = 'PROT12345'
        db.session.commit()
        
        # Criar autorização
        autorizacao = AutorizacaoCancelamento(
            arquivo_nome='AC001_01022023.txt',
            codigo_apresentante='001',
            nome_apresentante='BANCO TESTE',
            data_movimento=date(2023, 2, 1),
            quantidade_solicitacoes=1,
            status='Processado',
            usuario_id=1
        )
        db.session.add(autorizacao)
        db.session.commit()
        
        # Criar transação
        transacao = TransacaoAutorizacaoCancelamento(
            autorizacao_id=autorizacao.id,
            numero_protocolo='PROT12345',
            data_protocolizacao=date(2023, 2, 1),
            numero_titulo='1234567890',
            nome_devedor='DEVEDOR TESTE',
            valor_titulo=100.50,
            solicitacao_cancelamento='A',
            carteira_nosso_numero='67890',
            status='Pendente'
        )
        db.session.add(transacao)
        db.session.commit()
        transacao_id = transacao.id
    
    # Fazer a requisição de processamento
    response = client.post(f'/api/autorizacoes-cancelamento/transacoes/{transacao_id}/processar', 
                          headers=auth_headers())
    
    # Verificar se o processamento foi bem-sucedido
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'message' in response_data
    assert 'transacao' in response_data
    assert response_data['transacao']['status'] == 'Processado'
    
    # Verificar se o título foi atualizado
    with app.app_context():
        titulo = Titulo.query.filter_by(protocolo='PROT12345').first()
        assert titulo.status == 'Cancelado'


def test_gerar_arquivo_exemplo(client, auth_headers):
    """Testa a geração de um arquivo de exemplo"""
    # Fazer a requisição para gerar arquivo de exemplo
    response = client.get('/api/autorizacoes-cancelamento/gerar-arquivo-exemplo', 
                         headers=auth_headers())
    
    # Verificar se a geração foi bem-sucedida
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert 'Content-Disposition' in response.headers
    assert 'attachment' in response.headers['Content-Disposition']
    
    # Verificar o conteúdo do arquivo
    content = response.data.decode('latin-1')
    assert content.startswith('0')
    assert '1' in content
    assert content.endswith('4')