from datetime import datetime
from flask import request, jsonify, current_app
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import db
from app.models import User
from . import auth
from .middleware import auth_required, get_current_user

@auth.route('/login', methods=['POST'])
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
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login bem-sucedido
      401:
        description: Credenciais inválidas
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.verify_password(data.get('password')):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    if not user.ativo:
        return jsonify({'message': 'Usuário desativado. Contate o administrador.'}), 403
    
    # Atualizar último acesso
    user.ultimo_acesso = datetime.utcnow()
    db.session.commit()
    
    # Simplificando a resposta para retornar apenas os dados do usuário
    # sem token JWT para facilitar a autenticação
    return jsonify({
        'user': user.to_dict()
    }), 200

@auth.route('/me', methods=['GET'])
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
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict()), 200

@auth.route('/users', methods=['GET'])
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
    user_id = request.json.get('user_id')
    current_user = User.query.get(user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({'message': 'Acesso negado'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth.route('/users', methods=['POST'])
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
    user_id = request.json.get('user_id')
    current_user = User.query.get(user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({'message': 'Acesso negado'}), 403
    
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
    user_id = request.json.get('user_id')
    current_user = User.query.get(user_id)
    
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
    
    return jsonify(user.to_dict()), 200

@auth.route('/users/<int:id>', methods=['DELETE'])
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
    user_id = request.json.get('user_id')
    current_user = User.query.get(user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({'message': 'Acesso negado'}), 403
    
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Não permitir que um administrador remova a si mesmo
    if user.id == current_user.id:
        return jsonify({'message': 'Não é possível remover seu próprio usuário'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário removido com sucesso'}), 200

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
    if current_app.config['FLASK_ENV'] != 'development':
        return jsonify({'message': 'Rota não disponível em produção'}), 404
    
    data = request.get_json()
    
    if not data or data.get('secret_key') != 'dev_setup_key':
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