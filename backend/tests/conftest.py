import os
import sys
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token

# Adicionar o diretório raiz ao path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar os modelos diretamente do módulo app.models
from app.models import User, Titulo, Remessa, Credor, Devedor, Desistencia, Erro

# Importar a função create_app e db do arquivo app.py
import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(__file__), "../app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
create_app = app_module.create_app
db = app_module.db

@pytest.fixture
def app():
    """Cria e configura uma instância da aplicação Flask para testes"""
    # Usar a configuração de teste
    app = create_app('testing')
    
    # Criar um contexto de aplicação
    with app.app_context():
        # Criar todas as tabelas no banco de dados de teste
        db.create_all()
        yield app
        # Limpar o banco de dados após os testes
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Um cliente de teste para a aplicação"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Um runner de linha de comando para testar comandos Flask CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Gera headers de autenticação com um token JWT válido"""
    def _auth_headers(user_id=1):
        access_token = create_access_token(identity=user_id)
        return {'Authorization': f'Bearer {access_token}'}
    return _auth_headers

@pytest.fixture
def init_database(app):
    """Inicializa o banco de dados com dados de teste"""
    # Criar usuário de teste
    user = User(
        username='testuser',
        email='test@example.com',
        password='password123',
        nome_completo='Usuário de Teste',
        cargo='Analista',
        admin=True
    )
    db.session.add(user)
    
    # Criar credor de teste
    credor = Credor(
        nome='Empresa Credora Teste',
        documento='12345678901234',
        endereco='Rua Teste, 123',
        cidade='São Paulo',
        uf='SP',
        cep='01234-567'
    )
    db.session.add(credor)
    
    # Criar devedor de teste
    devedor = Devedor(
        nome='Devedor Teste',
        documento='98765432109',
        endereco='Avenida Teste, 456',
        cidade='Rio de Janeiro',
        uf='RJ',
        cep='21000-000'
    )
    db.session.add(devedor)
    
    # Criar remessa de teste
    remessa = Remessa(
        nome_arquivo='remessa_teste.txt',
        status='Processado',
        uf='SP',
        tipo='Remessa',
        quantidade_titulos=1,
        usuario_id=1
    )
    db.session.add(remessa)
    
    # Criar título de teste
    titulo = Titulo(
        numero='12345',
        protocolo='PROT12345',
        valor=1000.50,
        data_emissao='2023-01-01',
        data_vencimento='2023-02-01',
        status='Pendente',
        remessa_id=1,
        credor_id=1,
        devedor_id=1,
        especie='DMI',
        aceite=False,
        nosso_numero='67890'
    )
    db.session.add(titulo)
    
    db.session.commit()
    
    return {'user': user, 'credor': credor, 'devedor': devedor, 'remessa': remessa, 'titulo': titulo}