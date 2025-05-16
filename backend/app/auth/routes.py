from datetime import datetime
import os
import base64
from flask import request, jsonify, current_app, g # Adicionado g
from werkzeug.security import generate_password_hash # Não usado diretamente aqui, mas pode ser útil para User model
from app import db
from app.models import User
from . import auth
from .middleware import auth_required # Removida a importação de get_current_user

@auth.route("/login", methods=["POST", "OPTIONS"])
def login():
    """
    Endpoint para autenticação de usuários (Basic Auth)
    ---
    tags:
      - Autenticação
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Credenciais Basic Auth (ex: Basic dXNlcjpwYXNzd29yZA==)
    responses:
      200:
        description: Login bem-sucedido, usuário autenticado.
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              $ref: "#/definitions/User"
      401:
        description: Credenciais inválidas ou cabeçalho de autorização ausente/malformado.
    """
    # Tratamento para requisições OPTIONS com cabeçalhos CORS explícitos
    if request.method == "OPTIONS":
        response = jsonify({})
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '3600')
        return response

    # Para requisições POST, seguir com o fluxo de autenticação
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # Se o frontend não enviar o header, ele pode estar enviando no corpo (não ideal para Basic Auth)
        data = request.get_json()
        if not data:
            return jsonify({"message": "Dados de autenticação não fornecidos (esperado header Authorization ou JSON com email/senha)"}), 400
        email = data.get("email")
        senha = data.get("senha") or data.get("password")
        if not email or not senha:
            return jsonify({"message": "Email e senha são obrigatórios no corpo JSON se o header Authorization não for usado."}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(senha):
            return jsonify({"message": "Credenciais inválidas"}), 401
        if not user.ativo:
            return jsonify({"message": "Usuário desativado. Contate o administrador."}), 403
        
        # Atualizar último acesso
        user.ultimo_acesso = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Usuário {email} autenticado com sucesso via POST para /login.")
        response = jsonify({"message": "Login bem-sucedido", "user": user.to_dict()})
        
        # Garantir cabeçalhos CORS na resposta de sucesso
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response, 200

    # Se o header Authorization estiver presente, o middleware (se aplicado à rota) já teria validado.
    # Como não está, vamos validar aqui também.
    try:
        auth_type, credentials_b64 = auth_header.split(None, 1)
        if auth_type.lower() == "basic":
            credentials_bytes = base64.b64decode(credentials_b64)
            credentials_str = credentials_bytes.decode("iso-8859-1")
            username, password = credentials_str.split(":", 1)
            
            user = User.query.filter_by(email=username).first()
            if not user or not user.verify_password(password):
                return jsonify({"message": "Credenciais inválidas no header Authorization"}), 401
            if not user.ativo:
                return jsonify({"message": "Usuário desativado. Contate o administrador."}), 403
            
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"Usuário {username} autenticado com sucesso via header Authorization em /login.")
            response = jsonify({"message": "Login bem-sucedido", "user": user.to_dict()})
            
            # Garantir cabeçalhos CORS na resposta de sucesso
            origin = request.headers.get('Origin')
            if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            return response, 200
        else:
            return jsonify({"message": "Esquema de autenticação Basic esperado no header Authorization"}), 401
    except Exception as e:
        current_app.logger.error(f"Erro ao processar header Authorization em /login: {e}")
        return jsonify({"message": "Erro ao processar autenticação via header"}), 401

@auth.route("/me", methods=["GET"])
@auth_required()
def get_user_info():
    """
    Retorna informações do usuário autenticado (via Basic Auth)
    ---
    tags:
      - Autenticação
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    responses:
      200:
        description: Informações do usuário
        schema:
          $ref: "#/definitions/User"
      401:
        description: Não autenticado
      404:
        description: Usuário não encontrado (não deveria acontecer se autenticado)
    """
    user = getattr(g, "user", None) # Obter usuário do contexto da requisição (definido em middleware)
    
    if not user:
        # Isso não deveria acontecer se @auth_required funcionou corretamente
        return jsonify({"message": "Usuário não encontrado no contexto da requisição, mesmo após @auth_required."}), 404 
    
    return jsonify(user.to_dict()), 200

@auth.route("/users", methods=["GET"])
@auth_required(admin_required=True)
def get_users():
    """
    Lista todos os usuários (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    responses:
      200:
        description: Lista de usuários
      403:
        description: Acesso negado (não é admin)
      401:
        description: Não autenticado
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth.route("/users", methods=["POST"])
@auth_required(admin_required=True)
def create_user():
    """
    Cria um novo usuário (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - email
            - password
            - nome_completo
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            nome_completo:
              type: string
            cargo:
              type: string
            admin:
              type: boolean
    responses:
      201:
        description: Usuário criado
      400:
        description: Dados inválidos
      403:
        description: Acesso negado
      409:
        description: Usuário já existe
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ("username", "email", "password", "nome_completo")):
        return jsonify({"message": "Dados incompletos"}), 400
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Nome de usuário já existe"}), 409
    
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email já cadastrado"}), 409
    
    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"], # O model User deve hashear a senha ao setar
        nome_completo=data["nome_completo"],
        cargo=data.get("cargo"),
        admin=data.get("admin", False)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@auth.route("/users/<int:id>", methods=["PUT"])
@auth_required()
def update_user(id):
    """
    Atualiza um usuário existente
    ---
    tags:
      - Autenticação
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            nome_completo:
              type: string
            cargo:
              type: string
            admin:
              type: boolean
            ativo:
              type: boolean
    responses:
      200:
        description: Usuário atualizado
      403:
        description: Acesso negado
      404:
        description: Usuário não encontrado
    """
    current_user = getattr(g, "user", None) # Obter usuário do contexto da requisição
    
    if not current_user or (not current_user.admin and current_user.id != id):
        return jsonify({"message": "Acesso negado"}), 403
    
    user_to_update = User.query.get(id)
    if not user_to_update:
        return jsonify({"message": "Usuário não encontrado"}), 404
    
    data = request.get_json()
    
    if "username" in data and data["username"] != user_to_update.username:
        if User.query.filter(User.id != id, User.username == data["username"]).first():
            return jsonify({"message": "Nome de usuário já existe"}), 409
        user_to_update.username = data["username"]
    
    if "email" in data and data["email"] != user_to_update.email:
        if User.query.filter(User.id != id, User.email == data["email"]).first():
            return jsonify({"message": "Email já cadastrado"}), 409
        user_to_update.email = data["email"]
    
    if "password" in data and data["password"]:
        user_to_update.password = data["password"] # O model User deve hashear a senha
    
    if "nome_completo" in data:
        user_to_update.nome_completo = data["nome_completo"]
    
    if "cargo" in data:
        user_to_update.cargo = data["cargo"]
    
    if current_user.admin:
        if "admin" in data:
            user_to_update.admin = data["admin"]
        if "ativo" in data:
            user_to_update.ativo = data["ativo"]
    
    db.session.commit()
    
    # A função clear_user_cache foi mantida no middleware, mas sua lógica é um placeholder.
    # Se não houver cache real, esta chamada pode ser removida.
    from .middleware import clear_user_cache 
    clear_user_cache(user_to_update.id)
    
    return jsonify(user_to_update.to_dict()), 200

@auth.route("/users/<int:id>", methods=["DELETE"])
@auth_required(admin_required=True)
def delete_user(id):
    """
    Remove um usuário (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuário removido
      403:
        description: Acesso negado
      404:
        description: Usuário não encontrado
    """
    current_user = getattr(g, "user", None) # Obter usuário do contexto da requisição
    
    user_to_delete = User.query.get(id)
    if not user_to_delete:
        return jsonify({"message": "Usuário não encontrado"}), 404
    
    if user_to_delete.id == current_user.id:
        return jsonify({"message": "Não é possível remover seu próprio usuário"}), 400
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    return jsonify({"message": "Usuário removido com sucesso"}), 200

# A rota /refresh não faz sentido com Basic Auth, pois não há tokens para renovar.
# Removida.

@auth.route("/logout", methods=["POST", "OPTIONS"])
def logout(): # Não precisa de @auth_required, pois o cliente apenas "esquece" as credenciais
    """
    Endpoint para realizar logout (para Basic Auth, é mais um placeholder)
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Logout realizado com sucesso (cliente deve limpar credenciais)
    """
    # Tratamento para requisições OPTIONS com cabeçalhos CORS explícitos
    if request.method == "OPTIONS":
        response = jsonify({})
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '3600')
        return response
        
    # Com Basic Auth, o logout é responsabilidade do cliente (limpar o header Authorization ou as credenciais armazenadas)
    response = jsonify({"message": "Logout realizado com sucesso. O cliente deve limpar as credenciais Basic Auth."})
    
    # Garantir cabeçalhos CORS na resposta de sucesso
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
    return response, 200

@auth.route("/seed-admin", methods=["POST"])
def seed_admin():
    """
    Endpoint para criar usuário admin inicial (para desenvolvimento/setup)
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - secret_key
          properties:
            secret_key:
              type: string
    responses:
      201:
        description: Usuário admin criado
      400:
        description: Dados inválidos ou chave secreta não fornecida
      401:
        description: Chave secreta inválida
      409:
        description: Usuário admin já existe
    """
    data = request.get_json()
    
    if not data or "secret_key" not in data:
        return jsonify({"message": "Chave secreta não fornecida"}), 400
    
    # Use uma variável de ambiente para a chave secreta em produção
    expected_secret_key = os.environ.get("ADMIN_SEED_SECRET_KEY", "dev_setup_key") 
    if data["secret_key"] != expected_secret_key:
        return jsonify({"message": "Chave secreta inválida"}), 401
    
    if User.query.filter_by(email="admin@protestsystem.com").first():
        return jsonify({"message": "Usuário admin já existe"}), 409
    
    admin = User(
        username="admin",
        email="admin@protestsystem.com",
        password="admin123", # O model User deve hashear a senha
        nome_completo="Administrador",
        cargo="Administrador",
        admin=True,
        ativo=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    return jsonify({"message": "Usuário admin criado com sucesso"}), 201
