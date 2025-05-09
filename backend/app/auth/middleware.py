from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models import User
import time
import base64

# Cache simples para armazenar dados de usuário e reduzir consultas ao banco
_user_cache = {}
_cache_timeout = 300  # 5 minutos em segundos

def basic_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Cabeçalho de autorização ausente'}), 401

        try:
            auth_type, credentials_b64 = auth_header.split(None, 1)
        except ValueError:
            return jsonify({'message': 'Cabeçalho de autorização malformado'}), 401

        if auth_type.lower() != 'basic':
            return jsonify({'message': 'Esquema de autenticação Basic esperado'}), 401

        try:
            credentials_bytes = base64.b64decode(credentials_b64)
        except base64.binascii.Error:
            return jsonify({'message': 'Credenciais Base64 inválidas'}), 401

        try:
            credentials_str = credentials_bytes.decode('iso-8859-1')
            username, password = credentials_str.split(':', 1)
        except UnicodeDecodeError:
            return jsonify({'message': 'Erro ao decodificar credenciais com ISO-8859-1'}), 401
        except ValueError:
            return jsonify({'message': 'Formato de credenciais inválido (esperado usuário:senha)'}), 401

        user = User.query.filter_by(username=username).first() # Ou filter_by(email=username) dependendo do campo usado para login

        if not user or not user.verify_password(password) or not user.ativo:
            current_app.logger.warning(f"Falha na autenticação Basic para o usuário: {username}")
            return jsonify({'message': 'Credenciais inválidas ou usuário inativo'}), 401
        
        # Adicionar usuário ao contexto da requisição, se necessário, ou apenas permitir o acesso
        # g.current_user = user # Exemplo, se estiver usando flask.g
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
                # Verificar se o token JWT está presente no header ou cookie
                verify_jwt_in_request()
                
                # Obter o ID do usuário e claims adicionais do token JWT
                user_id = get_jwt_identity()
                claims = get_jwt()
                
                # Verificar se o usuário existe e está ativo usando cache quando possível
                user = get_current_user()
                if not user or not user.ativo:
                    return jsonify({'message': 'Usuário não encontrado ou inativo'}), 401
                
                # Verificar se o usuário é administrador, se necessário
                if admin_required and not user.admin:
                    return jsonify({'message': 'Acesso negado. Permissão de administrador necessária.'}), 403
                    
                # Continuar com a função original
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'message': 'Autenticação JWT necessária', 'error': str(e)}), 401
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
        
        # Verificar se o usuário está no cache e se o cache ainda é válido
        current_time = time.time()
        if user_id in _user_cache:
            cached_user, timestamp = _user_cache[user_id]
            if current_time - timestamp < _cache_timeout:
                return cached_user
        
        # Se não estiver no cache ou o cache expirou, buscar do banco
        user = User.query.get(user_id)
        if user:
            # Armazenar no cache
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

