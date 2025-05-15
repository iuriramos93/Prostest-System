from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_compress import Compress
from flask_caching import Cache
from config import config
from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager # Removido JWTManager
import os
import time

db = SQLAlchemy()
compress = Compress()
cache = Cache()
bcrypt = Bcrypt()
# jwt = JWTManager() # Removido JWTManager

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Configurar banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL') or
        'postgresql://postgres:postgres@db:5432/protest_system'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações JWT foram removidas
    # app.config['JWT_SECRET_KEY'] = app.config.get('JWT_SECRET_KEY', 'jwt-secret-string')
    # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
    # app.config['JWT_REFRESH_TOKEN_EXPIRES'] = app.config.get('JWT_REFRESH_TOKEN_EXPIRES')

    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    # jwt.init_app(app) # Removido JWTManager
    
    # Configurar CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    Migrate(app, db)
    Swagger(app)
    
    # Inicializar ferramentas de performance
    compress.init_app(app)
    
    # Configurar cache
    cache_config = {
        'CACHE_TYPE': 'SimpleCache',  # Em produção, use 'RedisCache'
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD': 1000  # Máximo de itens no cache
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)
    
    # Inicializar ferramentas de performance personalizadas
    from app.utils.performance import init_performance_tools
    init_performance_tools(app)
    
    # Inicializar sistema de tarefas assíncronas
    from app.utils.async_tasks import init_async_tasks
    init_async_tasks(app)

    # Adicionar endpoint de saúde
    @app.route('/health')
    def health_check():
        try:
            # Verificar conexão com banco de dados
            db.session.execute('SELECT 1')
            db_status = 'ok'
        except Exception as e:
            app.logger.error(f"Erro na verificação do banco de dados: {str(e)}")
            db_status = 'error'
        
        return {
            'status': 'ok' if db_status == 'ok' else 'error',
            'database': db_status,
            'timestamp': time.time()
        }

    # Registrar blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    from app.titulos import titulos as titulos_blueprint
    app.register_blueprint(titulos_blueprint, url_prefix='/api/titulos')

    from app.remessas import remessas as remessas_blueprint
    app.register_blueprint(remessas_blueprint, url_prefix='/api/remessas')

    from app.desistencias import desistencias as desistencias_blueprint
    app.register_blueprint(desistencias_blueprint, url_prefix='/api/desistencias')

    from app.erros import erros as erros_blueprint
    app.register_blueprint(erros_blueprint, url_prefix='/api/erros')

    from app.relatorios import relatorios as relatorios_blueprint
    app.register_blueprint(relatorios_blueprint, url_prefix='/api/relatorios')

    from app.autorizacoes_cancelamento import autorizacoes as autorizacoes_blueprint
    app.register_blueprint(autorizacoes_blueprint, url_prefix='/api/autorizacoes')

    from app.protestos import protestos as protestos_blueprint
    app.register_blueprint(protestos_blueprint, url_prefix='/api/protestos')

    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()

    return app

# Factory pattern implementation
# A instância é criada pelo wsgi.py

