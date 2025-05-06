import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_compress import Compress
from flasgger import Swagger
from config import config

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
compress = Compress()

def create_app(config_name=None):
    """Função factory para criar a aplicação Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    compress.init_app(app)
    
    # Configuração do CORS para permitir requisições do frontend
    # Definindo origens permitidas
    origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", 
               "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "http://127.0.0.1:3003"]
    
    CORS(app, 
         resources={r"/*": {"origins": origins}}, 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Configurar Swagger para documentação da API
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    Swagger(app, config=swagger_config)
    
    # Criar diretório de uploads se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    try:
        # Tentar importar os blueprints
        # Se falhar por falta de bibliotecas ou configuração, continuar com as rotas básicas
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
        app.register_blueprint(autorizacoes_blueprint, url_prefix='/api/autorizacoes-cancelamento')
    except ImportError as e:
        app.logger.warning(f"Não foi possível importar alguns blueprints: {str(e)}")
        app.logger.info("Continuando com as rotas básicas...")
    
    # Configurar headers CORS para todas as respostas
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
            
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Handler for OPTIONS requests (preflight)
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        return jsonify({}), 200
    
    # Rota para listar todas as rotas definidas
    @app.route('/api/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        return jsonify({'routes': routes})
    
    # Rota para verificar o status da conexão com o banco de dados
    @app.route('/api/database/status')
    def db_status():
        try:
            db.session.execute('SELECT 1')
            return jsonify({'status': 'connected'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return app

# Criar a instância da aplicação
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)