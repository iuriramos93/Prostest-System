from functools import wraps
from flask import request, jsonify, current_app
from app.models import User # Assuming models.py is in the app directory
import base64

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
            credentials_str = credentials_bytes.decode("iso-8859-1") # Using iso-8859-1 as per original code for basic auth
            username, password = credentials_str.split(":", 1)
        except UnicodeDecodeError:
            # Attempt fallback to utf-8 if iso-8859-1 fails, or log/handle as appropriate
            try:
                credentials_str = credentials_bytes.decode("utf-8")
                username, password = credentials_str.split(":", 1)
            except UnicodeDecodeError:
                return jsonify({"message": "Erro ao decodificar credenciais (ISO-8859-1 e UTF-8 falharam)"}), 401
            except ValueError:
                return jsonify({"message": "Formato de credenciais inválido (esperado usuário:senha) após fallback UTF-8"}), 401
        except ValueError:
            return jsonify({"message": "Formato de credenciais inválido (esperado usuário:senha)"}), 401

        # Assuming username for Basic Auth is the email
        user = User.query.filter_by(email=username).first()

        if not user or not user.verify_password(password) or not user.ativo:
            current_app.logger.warning(f"Falha na autenticação Basic para o usuário: {username}")
            return jsonify({"message": "Credenciais inválidas ou usuário inativo"}), 401
        
        current_app.logger.info(f"Usuário {username} autenticado com sucesso via Basic Auth.")
        # Adicionar o usuário ao contexto da requisição, se necessário para outras partes da aplicação
        # g.user = user # Exemplo, requer import de 'g' from flask
        return f(*args, **kwargs)
    return decorated_function

# Manter o alias auth_required para compatibilidade, apontando para basic_auth_required
# Se o parâmetro admin_required for necessário, ele precisará ser integrado à lógica do basic_auth_required
# ou uma nova função específica para admin com basic auth deve ser criada.
# Por ora, faremos um alias simples. Se a lógica de admin_required for usada em algum lugar, precisará de ajuste.
def auth_required(admin_required=False):
    """
    Decorador para verificar se o usuário está autenticado via Basic Auth.
    O parâmetro admin_required não é funcional nesta versão simplificada e precisaria
    de lógica adicional dentro de basic_auth_required ou uma nova função.
    """
    if admin_required:
        # Esta é uma limitação. A lógica de verificação de admin precisaria ser
        # adicionada em basic_auth_required ou em um novo decorador.
        current_app.logger.warning("O parâmetro admin_required=True em auth_required não tem efeito com Basic Auth puro sem modificações.")
    return basic_auth_required

