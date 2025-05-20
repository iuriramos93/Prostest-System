from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_compress import Compress
from flask_caching import Cache
from config import config
from flask_bcrypt import Bcrypt
import os
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
compress = Compress()
cache = Cache()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address)

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
    
    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    
    # Configuração CORS centralizada e unificada - EXPANDIDA para incluir todas as portas possíveis
    # Permitir requisições do frontend para o backend independente das variações de localhost/127.0.0.1
    allowed_origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
        "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta principal
        "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta alternativa
        "http://localhost:3000", "http://127.0.0.1:3000",  # Outras portas comuns
        "http://localhost:8080", "http://127.0.0.1:8080"   # Outras portas comuns
    ]
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         expose_headers=["Content-Type", "Authorization"])
    
    # Adicionar headers de segurança e CORS
    @app.after_request
    def add_headers(response):
        # Headers de segurança padrão
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Headers CORS - EXPANDIDO para todas as origens permitidas
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight por 1 hora
        
        return response
    
    # Tratar explicitamente requests OPTIONS para evitar redirecionamentos - MELHORADO
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        response = make_response()
        response.status_code = 200
        
        # Headers CORS para OPTIONS - EXPANDIDO
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight por 1 hora
        
        # Garantir que não haja redirecionamento
        return response, 200
    
    # Adicionar handler para erros HTTP para garantir headers CORS em todas as respostas
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    @app.errorhandler(301)
    @app.errorhandler(302)
    @app.errorhandler(307)
    @app.errorhandler(308)
    def handle_error(error):
        response = jsonify({
            'error': str(error), 
            'message': error.description if hasattr(error, 'description') else 'Erro no servidor'
        })
        response.status_code = error.code if hasattr(error, 'code') else 500
        
        # Headers CORS para erros - EXPANDIDO
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    # Adicionar handler para erros de rate limiting
    @app.errorhandler(429)
    def ratelimit_handler(e):
        response = jsonify({
            "error": "ratelimit_exceeded",
            "message": "Limite de requisições excedido. Por favor, tente novamente mais tarde.",
            "retry_after": e.description
        })
        response.status_code = 429
        
        # Headers CORS para erro de rate limiting
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    Migrate(app, db)
    
    # Configurar Swagger com autenticação Basic e CORS
    swagger_config = {
        "headers": [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
        ],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
        "securityDefinitions": {
            "BasicAuth": {
                "type": "basic"
            }
        },
    }
    Swagger(app, config=swagger_config)
    
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

    # Adicionar endpoint de saúde
    @app.route('/health')
    def health_check():
        try:
            # Verificar conexão com banco de dados
            db.session.execute(db.text('SELECT 1'))
            db_status = 'ok'
        except Exception as e:
            app.logger.error(f"Erro na verificação do banco de dados: {str(e)}")
            db_status = 'error'
        
        return {
            'status': 'ok' if db_status == 'ok' else 'error',
            'database': db_status,
            'timestamp': time.time(),
            'version': '1.0.0'
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
