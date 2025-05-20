from flask import Flask, g, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_name='development'):
    from config import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Configuração CORS centralizada com configurações mais permissivas
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
             "allow_headers": ["Content-Type", "Authorization"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "supports_credentials": False,  # Desabilitado para evitar problemas com preflight
             "expose_headers": ["Content-Type", "Authorization"]
         }})
    
    # Adicionar handler específico para OPTIONS para evitar redirecionamentos em preflight
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response
    
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
