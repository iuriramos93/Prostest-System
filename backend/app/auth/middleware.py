from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User # Assuming models.py is in the app directory
import time
import base64

# Cache simples para armazenar dados de usuário e reduzir consultas ao banco
_user_cache = {}
_cache_timeout = 300  # 5 minutos em segundos

def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "Cabeçalho de autorização ausente"}), 401

        try:
            auth_type, credentials_b64 = auth_header.split(None, 1)
        except ValueError:
            return jsonify({"message": "Cabeçalho de autorização malformado"}), 401

        if auth_type.lower() != "basic":
            return jsonify({"message": "Esquema de autenticação Basic esperado"}), 401

        try:
            credentials_bytes = base64.b64decode(credentials_b64)
        except base64.binascii.Error: # Corrected exception type
            return jsonify({"message": "Credenciais Base64 inválidas"}), 401

        try:
            credentials_str = credentials_bytes.decode("iso-8859-1")
            username, password = credentials_str.split(":", 1)
        except UnicodeDecodeError:
            return jsonify({"message": "Erro ao decodificar credenciais com ISO-8859-1"}), 401
        except ValueError:
            return jsonify({"message": "Formato de credenciais inválido (esperado usuário:senha)"}), 401

        # Assuming username for Basic Auth is the email
        user = User.query.filter_by(email=username).first()

        if not user or not user.verify_password(password) or not user.ativo:
            current_app.logger.warning(f"Falha na autenticação Basic para o usuário: {username}")
            return jsonify({"message": "Credenciais inválidas ou usuário inativo"}), 401
        
        current_app.logger.info(f"Usuário {username} autenticado com sucesso via Basic Auth.")
        return f(*args, **kwargs)
    return decorated_function

def auth_required(admin_required=False):
    """
    Decorador para verificar se o usuário está autenticado através do token JWT
    
    Parâmetros:
    - admin_required: Se True, verifica se o usuário é administrador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                # claims = get_jwt() # claims not used, can be removed if not needed later
                
                user = get_current_user()
                if not user or not user.ativo:
                    return jsonify({"message": "Usuário não encontrado ou inativo"}), 401
                
                if admin_required and not user.admin:
                    return jsonify({"message": "Acesso negado. Permissão de administrador necessária."}), 403
                    
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({"message": "Autenticação JWT necessária", "error": str(e)}), 401
        return decorated_function
    return decorator

def get_current_user():
    """
    Função para obter o usuário atual baseado no token JWT
    Utiliza cache para reduzir consultas ao banco de dados
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        current_time = time.time()
        if user_id in _user_cache:
            cached_user, timestamp = _user_cache[user_id]
            if current_time - timestamp < _cache_timeout:
                return cached_user
        
        user = User.query.get(user_id)
        if user:
            _user_cache[user_id] = (user, current_time)
        return user
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário atual (JWT): {str(e)}")
        return None

def clear_user_cache(user_id=None):
    """
    Limpa o cache de usuários
    
    Parâmetros:
    - user_id: Se fornecido, limpa apenas o cache deste usuário
    """
    global _user_cache
    if user_id is not None and user_id in _user_cache:
        del _user_cache[user_id]
    elif user_id is None:
        _user_cache = {}
    return True

