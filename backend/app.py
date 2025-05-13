import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from flask_compress import Compress
from flasgger import Swagger
from werkzeug.security import check_password_hash
from config import config

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
compress = Compress()

def create_app(config_name=None):
    """Função factory para criar a aplicação Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    compress.init_app(app)
    
    # Configuração do CORS para permitir requisições do frontend
    # Definindo origens permitidas
    origins = ["http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173", "http://127.0.0.1:3003", 
               "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173", "http://127.0.0.1:3003"]
    
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
    
    # Rota de teste para verificar se a API está funcionando
    @app.route('/api/health')
    def health_check():
        return {"status": "ok", "message": "API is running"}
    
    # Rota de login
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados não fornecidos'}), 400
            
            email = data.get('email')
            senha = data.get('senha')
            
            if not email or not senha:
                return jsonify({'error': 'Email e senha são obrigatórios'}), 400
            
            # Buscar usuário no banco de dados
            from app.models import User
            user = User.query.filter_by(email=email).first()
            
            if not user or not check_password_hash(user.password_hash, senha):
                return jsonify({'error': 'Credenciais inválidas'}), 401
            
            if not user.ativo:
                return jsonify({'error': 'Usuário inativo'}), 401
            
            # Criar token JWT
            access_token = create_access_token(identity=user.id)
            
            # Atualizar último acesso
            user.ultimo_acesso = db.func.current_timestamp()
            db.session.commit()
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'nome_completo': user.nome_completo,
                    'username': user.username,
                    'cargo': user.cargo,
                    'admin': user.admin
                }
            })
        except Exception as e:
            app.logger.error(f"Erro no login: {str(e)}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
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
    app.run(host='127.0.0.1', port=5000, debug=True)