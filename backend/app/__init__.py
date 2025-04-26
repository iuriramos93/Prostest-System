from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_compress import Compress
from flask_caching import Cache
from config import config

db = SQLAlchemy()
compress = Compress()
cache = Cache()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Inicializar extensões
    db.init_app(app)
    CORS(app)
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

    return app

# Factory pattern implementation
# A instância é criada pelo wsgi.py