from functools import wraps
from flask import request, jsonify, current_app, g
from app.models import User # Assuming models.py is in the app directory
import base64

def basic_auth_required_internal(f, admin_required_flag=False):
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
        except base64.binascii.Error:
            return jsonify({"message": "Credenciais Base64 inválidas"}), 401

        try:
            credentials_str = credentials_bytes.decode("iso-8859-1")
            username, password = credentials_str.split(":", 1)
        except UnicodeDecodeError:
            try:
                credentials_str = credentials_bytes.decode("utf-8")
                username, password = credentials_str.split(":", 1)
            except UnicodeDecodeError:
                return jsonify({"message": "Erro ao decodificar credenciais (ISO-8859-1 e UTF-8 falharam)"}), 401
            except ValueError:
                return jsonify({"message": "Formato de credenciais inválido (esperado usuário:senha) após fallback UTF-8"}), 401
        except ValueError:
            return jsonify({"message": "Formato de credenciais inválido (esperado usuário:senha)"}), 401

        user = User.query.filter_by(email=username).first()

        if not user or not user.verify_password(password) or not user.ativo:
            current_app.logger.warning(f"Falha na autenticação Basic para o usuário: {username}")
            return jsonify({"message": "Credenciais inválidas ou usuário inativo"}), 401
        
        if admin_required_flag and not user.admin:
            current_app.logger.warning(f"Usuário {username} não é admin, mas acesso de admin é requerido.")
            return jsonify({"message": "Acesso restrito a administradores"}), 403

        current_app.logger.info(f"Usuário {username} autenticado com sucesso via Basic Auth.")
        g.user = user # Armazena o usuário autenticado no contexto da requisição
        return f(*args, **kwargs)
    return decorated_function

def auth_required(admin_required=False):
    """
    Decorador para verificar se o usuário está autenticado via Basic Auth.
    Se admin_required for True, também verifica se o usuário é administrador.
    """
    def decorator(f):
        return basic_auth_required_internal(f, admin_required_flag=admin_required)
    return decorator

# Função para limpar cache de usuário (se ainda for relevante)
# Esta função era chamada em update_user. Se o cache for simples (ex: g.user),
# não há muito o que limpar entre requisições. Se houver um cache mais complexo,
# esta lógica precisaria ser revista.
# Por ora, vamos manter uma stub ou remover se não for usada.
def clear_user_cache(user_id):
    # Implementar lógica de limpeza de cache se necessário
    # Exemplo: se você estiver usando um cache externo como Redis
    current_app.logger.info(f"clear_user_cache chamada para user_id: {user_id}. Nenhuma ação de cache implementada.")
    pass

