import pytest
from datetime import datetime, timedelta
from app.models import User, Titulo, Remessa, Credor, Devedor, Desistencia, Erro
from app import db

def test_user_model(app):
    """Testa o modelo de usuário"""
    # Criar um novo usuário
    user = User(
        username='modeltest',
        email='model@test.com',
        password='testpassword',
        nome_completo='Teste de Modelo',
        cargo='Tester',
        admin=False
    )
    
    # Adicionar ao banco de dados
    db.session.add(user)
    db.session.commit()
    
    # Recuperar o usuário
    saved_user = User.query.filter_by(username='modeltest').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_user is not None
    assert saved_user.email == 'model@test.com'
    assert saved_user.nome_completo == 'Teste de Modelo'
    assert saved_user.cargo == 'Tester'
    assert saved_user.admin is False
    assert saved_user.ativo is True
    
    # Testar verificação de senha
    assert saved_user.verify_password('testpassword')
    assert not saved_user.verify_password('wrongpassword')
    
    # Testar conversão para dicionário
    user_dict = saved_user.to_dict()
    assert user_dict['username'] == 'modeltest'
    assert user_dict['email'] == 'model@test.com'
    assert user_dict['nome_completo'] == 'Teste de Modelo'
    
    # Testar que a senha não é legível
    with pytest.raises(AttributeError):
        password = saved_user.password

def test_titulo_model(app, init_database):
    """Testa o modelo de título"""
    # Criar um novo título
    titulo = Titulo(
        numero='T12345',
        protocolo='PROT-T12345',
        valor=1500.75,
        data_emissao=datetime.now().date() - timedelta(days=30),
        data_vencimento=datetime.now().date() - timedelta(days=15),
        status='Pendente',
        remessa_id=init_database['remessa'].id,
        credor_id=init_database['credor'].id,
        devedor_id=init_database['devedor'].id,
        especie='DMI',
        aceite=True,
        nosso_numero='NT12345'
    )
    
    # Adicionar ao banco de dados
    db.session.add(titulo)
    db.session.commit()
    
    # Recuperar o título
    saved_titulo = Titulo.query.filter_by(protocolo='PROT-T12345').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_titulo is not None
    assert saved_titulo.numero == 'T12345'
    assert float(saved_titulo.valor) == 1500.75
    assert saved_titulo.status == 'Pendente'
    assert saved_titulo.especie == 'DMI'
    assert saved_titulo.aceite is True
    
    # Verificar relacionamentos
    assert saved_titulo.remessa.id == init_database['remessa'].id
    assert saved_titulo.credor.id == init_database['credor'].id
    assert saved_titulo.devedor.id == init_database['devedor'].id
    
    # Testar conversão para dicionário
    titulo_dict = saved_titulo.to_dict()
    assert titulo_dict['numero'] == 'T12345'
    assert titulo_dict['protocolo'] == 'PROT-T12345'
    assert float(titulo_dict['valor']) == 1500.75

def test_remessa_model(app, init_database):
    """Testa o modelo de remessa"""
    # Criar uma nova remessa
    remessa = Remessa(
        nome_arquivo='remessa_model_test.txt',
        status='Pendente',
        uf='MG',
        tipo='Remessa',
        quantidade_titulos=5,
        usuario_id=init_database['user'].id
    )
    
    # Adicionar ao banco de dados
    db.session.add(remessa)
    db.session.commit()
    
    # Recuperar a remessa
    saved_remessa = Remessa.query.filter_by(nome_arquivo='remessa_model_test.txt').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_remessa is not None
    assert saved_remessa.status == 'Pendente'
    assert saved_remessa.uf == 'MG'
    assert saved_remessa.tipo == 'Remessa'
    assert saved_remessa.quantidade_titulos == 5
    
    # Verificar relacionamentos
    assert saved_remessa.usuario_id == init_database['user'].id
    
    # Testar conversão para dicionário
    remessa_dict = saved_remessa.to_dict()
    assert remessa_dict['nome_arquivo'] == 'remessa_model_test.txt'
    assert remessa_dict['status'] == 'Pendente'
    assert remessa_dict['uf'] == 'MG'

def test_credor_devedor_models(app):
    """Testa os modelos de credor e devedor"""
    # Criar um novo credor
    credor = Credor(
        nome='Credor Modelo Teste',
        documento='12345678901234',
        endereco='Rua do Credor, 123',
        cidade='Cidade do Credor',
        uf='SP',
        cep='01234-567'
    )
    
    # Criar um novo devedor
    devedor = Devedor(
        nome='Devedor Modelo Teste',
        documento='98765432109876',
        endereco='Rua do Devedor, 456',
        cidade='Cidade do Devedor',
        uf='RJ',
        cep='21000-000'
    )
    
    # Adicionar ao banco de dados
    db.session.add_all([credor, devedor])
    db.session.commit()
    
    # Recuperar o credor e o devedor
    saved_credor = Credor.query.filter_by(documento='12345678901234').first()
    saved_devedor = Devedor.query.filter_by(documento='98765432109876').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_credor is not None
    assert saved_credor.nome == 'Credor Modelo Teste'
    assert saved_credor.cidade == 'Cidade do Credor'
    assert saved_credor.uf == 'SP'
    
    assert saved_devedor is not None
    assert saved_devedor.nome == 'Devedor Modelo Teste'
    assert saved_devedor.cidade == 'Cidade do Devedor'
    assert saved_devedor.uf == 'RJ'
    
    # Testar conversão para dicionário
    credor_dict = saved_credor.to_dict()
    devedor_dict = saved_devedor.to_dict()
    
    assert credor_dict['nome'] == 'Credor Modelo Teste'
    assert credor_dict['documento'] == '12345678901234'
    
    assert devedor_dict['nome'] == 'Devedor Modelo Teste'
    assert devedor_dict['documento'] == '98765432109876'

def test_desistencia_model(app, init_database):
    """Testa o modelo de desistência"""
    # Criar uma nova desistência
    desistencia = Desistencia(
        titulo_id=init_database['titulo'].id,
        motivo='Motivo de teste do modelo',
        observacoes='Observações de teste do modelo',
        status='Pendente',
        usuario_id=init_database['user'].id
    )
    
    # Adicionar ao banco de dados
    db.session.add(desistencia)
    db.session.commit()
    
    # Recuperar a desistência
    saved_desistencia = Desistencia.query.filter_by(motivo='Motivo de teste do modelo').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_desistencia is not None
    assert saved_desistencia.observacoes == 'Observações de teste do modelo'
    assert saved_desistencia.status == 'Pendente'
    
    # Verificar relacionamentos
    assert saved_desistencia.titulo_id == init_database['titulo'].id
    assert saved_desistencia.usuario_id == init_database['user'].id
    
    # Testar aprovação
    saved_desistencia.status = 'Aprovada'
    saved_desistencia.data_processamento = datetime.utcnow()
    saved_desistencia.usuario_processamento_id = init_database['user'].id
    db.session.commit()
    
    updated_desistencia = Desistencia.query.get(saved_desistencia.id)
    assert updated_desistencia.status == 'Aprovada'
    assert updated_desistencia.data_processamento is not None

def test_erro_model(app, init_database):
    """Testa o modelo de erro"""
    # Criar um novo erro
    erro = Erro(
        remessa_id=init_database['remessa'].id,
        titulo_id=init_database['titulo'].id,
        codigo='E999',
        descricao='Descrição do erro de teste',
        linha=100,
        status='Pendente'
    )
    
    # Adicionar ao banco de dados
    db.session.add(erro)
    db.session.commit()
    
    # Recuperar o erro
    saved_erro = Erro.query.filter_by(codigo='E999').first()
    
    # Verificar se os dados foram salvos corretamente
    assert saved_erro is not None
    assert saved_erro.descricao == 'Descrição do erro de teste'
    assert saved_erro.linha == 100
    assert saved_erro.status == 'Pendente'
    
    # Verificar relacionamentos
    assert saved_erro.remessa_id == init_database['remessa'].id
    assert saved_erro.titulo_id == init_database['titulo'].id
    
    # Testar resolução do erro
    saved_erro.status = 'Resolvido'
    saved_erro.observacao = 'Erro resolvido durante teste'
    saved_erro.data_resolucao = datetime.utcnow()
    db.session.commit()
    
    updated_erro = Erro.query.get(saved_erro.id)
    assert updated_erro.status == 'Resolvido'
    assert updated_erro.observacao == 'Erro resolvido durante teste'
    assert updated_erro.data_resolucao is not None