"""
Configuração CORS centralizada para o sistema
"""
from flask import Flask, request
from flask_cors import CORS

def configure_cors(app: Flask):
    """
    Configura as políticas CORS para a aplicação Flask
    
    Args:
        app: Instância da aplicação Flask
    """
    # Lista de origens permitidas
    allowed_origins = app.config.get('CORS_ALLOWED_ORIGINS', [
        "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
        "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta padrão
        "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta alternativa
        "http://localhost:3000", "http://127.0.0.1:3000",  # Porta alternativa React
        "http://localhost:8080", "http://127.0.0.1:8080",  # Porta alternativa Vue/outros
    ])
    
    # Cabeçalhos permitidos
    allowed_headers = [
        "Content-Type", 
        "Authorization", 
        "X-Requested-With", 
        "Accept", 
        "Origin",
        "Cache-Control",
        "X-CSRF-Token"
    ]
    
    # Métodos permitidos
    allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    
    # Configuração CORS global usando Flask-CORS
    CORS(app, 
        origins=allowed_origins,
        supports_credentials=True,
        allow_headers=allowed_headers,
        methods=allowed_methods,
        expose_headers=["Content-Type", "Authorization"],
        max_age=3600)  # Cache preflight por 1 hora
    
    # Handler para requisições OPTIONS (para garantir que sempre retornem 200)
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        response = app.make_response('')
        origin = request.headers.get('Origin')
        
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
            response.headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            
        response.status_code = 200
        return response
    
    # Garantir que as respostas de erro também tenham headers CORS
    @app.after_request
    def add_cors_headers(response):
        # Se já existir um header Access-Control-Allow-Origin, não fazer nada
        if 'Access-Control-Allow-Origin' in response.headers:
            return response
        
        origin = request.headers.get('Origin')
        
        # Se a origem estiver na lista de permitidas, adicionar headers CORS
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
            response.headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
        # Garantir que requisições OPTIONS retornem 200
        if request.method == 'OPTIONS':
            response.status_code = 200
            
        return response 