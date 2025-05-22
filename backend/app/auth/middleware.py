from functools import wraps
from flask import request, jsonify, g
import base64
from app.models import User

def auth_required(admin_required=False):
    """
    Decorator para autenticação Basic Auth
    
    Parâmetros:
    - admin_required: Se True, apenas usuários administradores podem acessar
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'message': 'Autenticação necessária'}), 401
            
            try:
                # Formato esperado: "Basic <credenciais_base64>"
                auth_type, credentials = auth_header.split(' ', 1)
                
                if auth_type.lower() != 'basic':
                    return jsonify({'message': 'Tipo de autenticação inválido. Use Basic Auth'}), 401
                
                # Decodificar credenciais
                decoded = base64.b64decode(credentials).decode('utf-8')
                username, password = decoded.split(':', 1)
                
                # Buscar usuário
                user = User.query.filter_by(username=username).first()
                
                if not user or not user.verify_password(password):
                    return jsonify({'message': 'Credenciais inválidas'}), 401
                
                if not user.ativo:
                    return jsonify({'message': 'Usuário inativo'}), 403
                
                if admin_required and not user.admin:
                    return jsonify({'message': 'Acesso restrito a administradores'}), 403
                
                # Armazenar usuário no contexto da requisição
                g.user = user
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'message': f'Erro de autenticação: {str(e)}'}), 401
        
        return decorated_function
    
    return decorator

def clear_user_cache(user_id):
    """
    Limpa o cache relacionado a um usuário específico
    
    Parâmetros:
    - user_id: ID do usuário
    """
    # Implementação de limpeza de cache (placeholder)
    # Em uma implementação real, isso limparia o cache do Redis ou similar
    pass
