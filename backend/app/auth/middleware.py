from functools import wraps
from flask import request, jsonify
from app.models import User

def auth_required():
    """
    Decorador para substituir o jwt_required
    Verifica se o usuário está autenticado através do user_id no JSON da requisição
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar se o user_id está presente no JSON da requisição
            user_id = request.json.get('user_id') if request.is_json else None
            
            if not user_id:
                return jsonify({'message': 'Autenticação necessária'}), 401
            
            # Verificar se o usuário existe e está ativo
            user = User.query.get(user_id)
            if not user or not user.ativo:
                return jsonify({'message': 'Usuário não encontrado ou inativo'}), 401
                
            # Continuar com a função original
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """
    Função para substituir get_jwt_identity
    Retorna o usuário atual baseado no user_id do JSON da requisição
    """
    user_id = request.json.get('user_id') if request.is_json else None
    if user_id:
        return User.query.get(user_id)
    return None