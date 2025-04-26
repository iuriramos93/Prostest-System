from datetime import datetime
import os
from flask import request, jsonify, current_app
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import db
from app.models import User
from . import auth
from .middleware import auth_required, get_current_user

@auth.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Endpoint para autenticação de usuários
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - senha
          properties:
            email:
              type: string
            senha:
              type: string
    responses:
      200:
        description: Login bem-sucedido
      401:
        description: Credenciais inválidas
    """
    # Tratamento para requisições OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        response = current_app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    data = request.get_json()
    
    # Verificar se os dados foram enviados corretamente
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400
    
    # Verificar os campos email e senha (ou password)
    email = data.get('email')
    # Verificar ambos os campos possíveis: senha (frontend) ou password (documentação)
    senha = data.get('senha') or data.get('password')
    
    if not email or not senha:
        return jsonify({'message': 'Dados incompletos. Email e senha são obrigatórios.'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.verify_password(senha):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    if not user.ativo:
        return jsonify({'message': 'Usuário desativado. Contate o administrador.'}), 403
    
    # Atualizar último acesso
    user.ultimo_acesso = datetime.utcnow()
    db.session.commit()
    
    # Importar os módulos JWT para gerar os tokens
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    # Dados do usuário para armazenar no token (minimizar tamanho)
    user_claims = {
        'id': user.id,
        'username': user.username,
        'admin': user.admin
    }
    
    # Gerar tokens JWT
    access_token = create_access_token(identity=user.id, additional_claims=user_claims)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Configurar resposta com headers CORS adequados
    response = jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token': access_token  # Adicionado para compatibilidade com frontend
    })
    
    # Configurar cookies seguros para os tokens
    secure = current_app.config.get('JWT_COOKIE_SECURE', False)
    response.set_cookie('access_token_cookie', access_token, 
                        httponly=True, secure=secure, 
                        samesite='Lax', max_age=86400)
    response.set_cookie('refresh_token_cookie', refresh_token, 
                        httponly=True, secure=secure, 
                        samesite='Lax', max_age=604800)
    
    return response, 200

@auth.route('/me', methods=['GET'])
@auth_required()
def get_user_info():
    """
    Retorna informações do usuário autenticado
    ---
    tags:
      - Autenticação
    security:
      - JWT: []
    responses:
      200:
        description: Informações do usuário
      404:
        description: Usuário não encontrado
    """
    user = get_current_user()
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict()), 200

@auth.route('/users', methods=['GET'])
@auth_required(admin_required=True)
def get_users():
    """
    Lista todos os usuários (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - JWT: []
    responses:
      200:
        description: Lista de usuários
      403:
        description: Acesso negado
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth.route('/users', methods=['POST'])
@auth_required(admin_required=True)
def create_user():
    """
    Cria um novo usuário (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - JWT: []
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
    
    if not data or not all(k in data for k in ('username', 'email', 'password', 'nome_completo')):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Nome de usuário já existe'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email já cadastrado'}), 409
    
    # Criar novo usuário
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        nome_completo=data['nome_completo'],
        cargo=data.get('cargo'),
        admin=data.get('admin', False)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@auth.route('/users/<int:id>', methods=['PUT'])
@auth_required()
def update_user(id):
    """
    Atualiza um usuário existente
    ---
    tags:
      - Autenticação
    security:
      - JWT: []
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
    current_user = get_current_user()
    
    # Apenas administradores podem atualizar outros usuários
    # Usuários normais só podem atualizar seu próprio perfil
    if not current_user or (not current_user.admin and current_user.id != id):
        return jsonify({'message': 'Acesso negado'}), 403
    
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    
    # Atualizar campos
    if 'username' in data and data['username'] != user.username:
        # Verificar se o novo username já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Nome de usuário já existe'}), 409
        user.username = data['username']
    
    if 'email' in data and data['email'] != user.email:
        # Verificar se o novo email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já cadastrado'}), 409
        user.email = data['email']
    
    if 'password' in data and data['password']:
        user.password = data['password']
    
    if 'nome_completo' in data:
        user.nome_completo = data['nome_completo']
    
    if 'cargo' in data:
        user.cargo = data['cargo']
    
    # Apenas administradores podem alterar status de admin e ativo
    if current_user.admin:
        if 'admin' in data:
            user.admin = data['admin']
        
        if 'ativo' in data:
            user.ativo = data['ativo']
    
    db.session.commit()
    
    # Limpar o cache do usuário para forçar uma nova consulta
    from .middleware import clear_user_cache
    clear_user_cache(user.id)
    
    return jsonify(user.to_dict()), 200

@auth.route('/users/<int:id>', methods=['DELETE'])
@auth_required(admin_required=True)
def delete_user(id):
    """
    Remove um usuário (apenas para administradores)
    ---
    tags:
      - Autenticação
    security:
      - JWT: []
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
    current_user = get_current_user()
    
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Não permitir que um administrador remova a si mesmo
    if user.id == current_user.id:
        return jsonify({'message': 'Não é possível remover seu próprio usuário'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário removido com sucesso'}), 200

@auth.route('/refresh', methods=['POST'])
def refresh():
    """
    Endpoint para renovar o token de acesso usando um refresh token
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
    responses:
      200:
        description: Token renovado com sucesso
      401:
        description: Token inválido ou expirado
    """
    from flask_jwt_extended import get_jwt_identity, create_access_token, verify_jwt_in_request, get_jwt
    
    # Verificar se o refresh token foi enviado
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        # Tentar obter do cookie
        refresh_token = request.cookies.get('refresh_token_cookie')
        if not refresh_token:
            return jsonify({'message': 'Refresh token não fornecido'}), 400
    else:
        refresh_token = data.get('refresh_token')
    
    try:
        # Verificar o refresh token
        from flask_jwt_extended import decode_token
        decoded_token = decode_token(refresh_token)
        user_id = decoded_token['sub']
        
        # Buscar o usuário
        user = User.query.get(user_id)
        if not user or not user.ativo:
            return jsonify({'message': 'Usuário inválido ou inativo'}), 401
        
        # Dados do usuário para armazenar no token (minimizar tamanho)
        user_claims = {
            'id': user.id,
            'username': user.username,
            'admin': user.admin
        }
        
        # Gerar novo token de acesso
        access_token = create_access_token(identity=user.id, additional_claims=user_claims)
        
        # Configurar resposta
        response = jsonify({
            'access_token': access_token,
            'token': access_token  # Para compatibilidade com frontend
        })
        
        # Configurar cookie seguro para o novo token
        secure = current_app.config.get('JWT_COOKIE_SECURE', False)
        response.set_cookie('access_token_cookie', access_token, 
                            httponly=True, secure=secure, 
                            samesite='Lax', max_age=86400)
        
        return response, 200
    except Exception as e:
        return jsonify({'message': 'Token inválido ou expirado', 'error': str(e)}), 401

@auth.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint para realizar logout
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Logout realizado com sucesso
    """
    response = jsonify({'message': 'Logout realizado com sucesso'})
    
    # Remover cookies de autenticação
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('refresh_token_cookie')
    
    return response, 200

@auth.route('/seed-admin', methods=['POST'])
def seed_admin():
    """
    Cria um usuário administrador inicial (apenas para ambiente de desenvolvimento)
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
        description: Administrador criado
      400:
        description: Chave secreta inválida
      409:
        description: Administrador já existe
    """
    # Esta rota só deve estar disponível em ambiente de desenvolvimento
    if os.environ.get('FLASK_ENV') != 'development':
        return jsonify({'message': 'Rota não disponível em produção'}), 404
    
    data = request.get_json()
    
    # Obter a chave secreta do ambiente ou usar o valor padrão apenas para desenvolvimento
    dev_key = os.environ.get('DEV_SETUP_KEY', 'dev_setup_key')
    
    if not data or data.get('secret_key') != dev_key:
        return jsonify({'message': 'Chave secreta inválida'}), 400
    
    # Verificar se já existe algum administrador
    if User.query.filter_by(admin=True).first():
        return jsonify({'message': 'Administrador já existe'}), 409
    
    # Criar usuário administrador
    admin = User(
        username='admin',
        email='admin@example.com',
        password='admin123',
        nome_completo='Administrador do Sistema',
        cargo='Administrador',
        admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    return jsonify(admin.to_dict()), 201