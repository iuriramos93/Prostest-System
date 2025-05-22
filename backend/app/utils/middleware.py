"""
Middlewares para aplicação Flask
"""
from flask import request, Response
from werkzeug.wrappers import Request

class PreflightMiddleware:
    """
    Middleware para tratar requisições preflight OPTIONS
    e evitar redirecionamentos que causam problemas CORS
    """
    
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        # Verificar se é uma requisição OPTIONS
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            # Obter a origem da requisição
            headers = {
                key[5:].replace('_', '-').lower(): value
                for key, value in environ.items()
                if key.startswith('HTTP_')
            }
            origin = headers.get('origin')
            
            # Obter origens permitidas da configuração da aplicação
            allowed_origins = []
            if hasattr(self.app, 'config'):
                allowed_origins = self.app.config.get('CORS_ALLOWED_ORIGINS', [])
            
            # Se não houver configuração específica, permitir todas as origens
            if not allowed_origins:
                allowed_origins = ['*']
            
            # Verificar se a origem é permitida
            is_allowed = origin in allowed_origins or '*' in allowed_origins
            
            if is_allowed:
                # Responder diretamente à requisição OPTIONS sem passar para o Flask
                response_headers = [
                    ('Access-Control-Allow-Origin', origin if origin else '*'),
                    ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH'),
                    ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, X-CSRF-Token'),
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Access-Control-Max-Age', '3600'),
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', '0')
                ]
                start_response('200 OK', response_headers)
                return [b'']
        
        # Para outras requisições, continuar o processamento normal
        return self.app(environ, start_response)

class CORSHeadersMiddleware:
    """
    Middleware para garantir que todas as respostas tenham os headers CORS corretos
    """
    
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        # Criar uma função wrapper para start_response que adiciona headers CORS
        def cors_start_response(status, headers, exc_info=None):
            # Obter a origem da requisição
            req_headers = {
                key[5:].replace('_', '-').lower(): value
                for key, value in environ.items()
                if key.startswith('HTTP_')
            }
            origin = req_headers.get('origin')
            
            # Obter origens permitidas da configuração da aplicação
            allowed_origins = []
            if hasattr(self.app, 'config'):
                allowed_origins = self.app.config.get('CORS_ALLOWED_ORIGINS', [])
            
            # Se não houver configuração específica, permitir todas as origens
            if not allowed_origins:
                allowed_origins = ['*']
            
            # Verificar se a origem é permitida
            if origin in allowed_origins or '*' in allowed_origins:
                # Converter headers para um dicionário para facilitar a manipulação
                headers_dict = dict(headers)
                
                # Adicionar headers CORS se não existirem
                if 'Access-Control-Allow-Origin' not in headers_dict:
                    headers.append(('Access-Control-Allow-Origin', origin if origin else '*'))
                
                if 'Access-Control-Allow-Methods' not in headers_dict:
                    headers.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH'))
                
                if 'Access-Control-Allow-Headers' not in headers_dict:
                    headers.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, X-CSRF-Token'))
                
                if 'Access-Control-Allow-Credentials' not in headers_dict:
                    headers.append(('Access-Control-Allow-Credentials', 'true'))
                
                # Para requisições OPTIONS, garantir status 200
                if environ.get('REQUEST_METHOD') == 'OPTIONS' and status.startswith('3'):  # Redirecionamento
                    status = '200 OK'
                    headers = [
                        ('Access-Control-Allow-Origin', origin if origin else '*'),
                        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH'),
                        ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, X-CSRF-Token'),
                        ('Access-Control-Allow-Credentials', 'true'),
                        ('Access-Control-Max-Age', '3600'),
                        ('Content-Type', 'text/plain'),
                        ('Content-Length', '0')
                    ]
            
            # Chamar a função original start_response
            return start_response(status, headers, exc_info)
        
        # Chamar a aplicação com o wrapper de start_response
        return self.app(environ, cors_start_response)

def register_middlewares(app):
    """
    Registra todos os middlewares na aplicação Flask
    
    Args:
        app: Instância da aplicação Flask
    """
    # Adicionar middleware de preflight
    app.wsgi_app = PreflightMiddleware(app.wsgi_app)
    
    # Adicionar middleware para garantir headers CORS em todas as respostas
    app.wsgi_app = CORSHeadersMiddleware(app.wsgi_app) 