from flask import Flask, jsonify, request, g, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
import os
import sys
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException

# Adicionar diretório pai ao path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar configurações
from config.environments import config
from config.cors import configure_cors
from app.utils.middleware import register_middlewares

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

# Configuração do Flask-Limiter com Redis para produção ou memória para desenvolvimento
def get_limiter(app=None):
    storage_uri = os.environ.get('REDIS_URL', 'memory://')
    if app and app.config.get('ENV') == 'production' and 'memory:' in storage_uri:
        app.logger.warning("Usando armazenamento em memória para rate limiting em produção. Considere configurar REDIS_URL.")
    
    return Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=storage_uri
    )

limiter = get_limiter()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuração
    if config_name == 'production':
        app.config.from_object(config['production'])
    else:
        app.config.from_object(config['development'])
    
    # Sobrescrever configurações com variáveis de ambiente
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI'))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config.get('SECRET_KEY'))
    
    # Lista de origens permitidas para CORS
    app.config['CORS_ALLOWED_ORIGINS'] = [
        "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
        "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta padrão
        "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta alternativa
        "http://localhost:3000", "http://127.0.0.1:3000",  # Porta alternativa React
        "http://localhost:8080", "http://127.0.0.1:8080",  # Porta alternativa Vue/outros
    ]
    
    # Registrar middlewares
    register_middlewares(app)
    
    # Configuração CORS centralizada
    configure_cors(app)
    
    # Inicializar extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)
    
    # Registrar blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    
    from app.remessas import remessas as remessas_blueprint
    app.register_blueprint(remessas_blueprint, url_prefix='/api/remessas')
    
    from app.titulos import titulos as titulos_blueprint
    app.register_blueprint(titulos_blueprint, url_prefix='/api/titulos')
    
    from app.desistencias import desistencias as desistencias_blueprint
    app.register_blueprint(desistencias_blueprint, url_prefix='/api/desistencias')
    
    from app.erros import erros as erros_blueprint
    app.register_blueprint(erros_blueprint, url_prefix='/api/erros')
    
    from app.relatorios import relatorios as relatorios_blueprint
    app.register_blueprint(relatorios_blueprint, url_prefix='/api/relatorios')
    
    # Handler para erros HTTP
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response
    
    # Handler para erros não-HTTP
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Registrar o erro
        app.logger.error(f"Erro não tratado: {str(e)}")
        
        # Criar resposta
        response = jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": "Ocorreu um erro interno no servidor."
        })
        response.status_code = 500
        return response
    
    # Headers de segurança
    @app.after_request
    def add_security_headers(response):
        # Headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    # Criar diretórios necessários
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Verificar conexão com o banco (usando método moderno do SQLAlchemy)
        try:
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            app.logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        except Exception as e:
            app.logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    
    return app
