from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import User
from app.auth.middleware import auth_required
from flask_pydantic import validate
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime
from functools import wraps

# Criação do blueprint com versionamento
api_v1 = Blueprint('api_v1_users', __name__, url_prefix='/api/v1')

# Modelos Pydantic para validação
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    nome_completo: str = Field(..., min_length=3, max_length=100)
    cargo: Optional[str] = Field(None, max_length=50)
    admin: bool = False
    ativo: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=64)
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=100)
    cargo: Optional[str] = Field(None, max_length=50)
    admin: Optional[bool] = None
    ativo: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: int
    data_criacao: datetime
    ultimo_acesso: Optional[datetime] = None

# Função para padronizar respostas da API
def api_response(data=None, message=None, status_code=200, errors=None):
    response = {
        "status": "success" if status_code < 400 else "error",
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": "1.0"
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
        
    if errors:
        response["errors"] = errors
        
    return jsonify(response), status_code

# Decorador para operações de banco de dados
def db_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro na operação de banco: {str(e)}")
            raise
    return wrapper

# Rotas da API
@api_v1.route('/users', methods=['GET'])
@auth_required()
def get_users():
    """
    Lista todos os usuários com filtros opcionais e paginação
    ---
    tags:
      - Usuários
    security:
      - BasicAuth: []
    parameters:
      - name: username
        in: query
        type: string
        required: false
        description: Nome de usuário
      - name: ativo
        in: query
        type: boolean
        required: false
        description: Status do usuário
      - name: page
        in: query
        type: integer
        required: false
        description: Número da página (começa em 1)
        default: 1
      - name: per_page
        in: query
        type: integer
        required: false
        description: Itens por página
        default: 10
    responses:
      200:
        description: Lista de usuários paginada
    """
    # Obter parâmetros de consulta
    username = request.args.get('username')
    ativo = request.args.get('ativo', type=bool)
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Construir a consulta usando SQLAlchemy 2.0
    stmt = db.select(User)
    
    # Aplicar filtros
    if username:
        stmt = stmt.where(User.username.ilike(f'%{username}%'))
    
    if ativo is not None:
        stmt = stmt.where(User.ativo == ativo)
    
    # Executar a consulta paginada
    pagination = db.paginate(stmt, page=page, per_page=per_page)
    
    # Preparar resposta
    response_data = {
        "items": [user.to_dict() for user in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }
    
    return api_response(data=response_data)

@api_v1.route('/users/<int:id>', methods=['GET'])
@auth_required()
def get_user(id):
    """
    Obtém detalhes de um usuário específico
    ---
    tags:
      - Usuários
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do usuário
    responses:
      200:
        description: Detalhes do usuário
      404:
        description: Usuário não encontrado
    """
    # Buscar o usuário pelo ID usando SQLAlchemy 2.0
    stmt = db.select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    if not user:
        return api_response(message="Usuário não encontrado", status_code=404)
    
    return api_response(data=user.to_dict())

@api_v1.route('/users', methods=['POST'])
@auth_required()
@validate()
@db_operation
def create_user(body: UserCreate):
    """
    Cria um novo usuário
    ---
    tags:
      - Usuários
    security:
      - BasicAuth: []
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserCreate'
    responses:
      201:
        description: Usuário criado
      400:
        description: Dados inválidos
    """
    # Verificar se username ou email já existem
    username_exists = db.session.execute(
        db.select(User).where(User.username == body.username)
    ).scalar_one_or_none()
    
    if username_exists:
        return api_response(
            message="Nome de usuário já existe",
            status_code=400,
            errors={"username": "Este nome de usuário já está em uso"}
        )
    
    email_exists = db.session.execute(
        db.select(User).where(User.email == body.email)
    ).scalar_one_or_none()
    
    if email_exists:
        return api_response(
            message="Email já existe",
            status_code=400,
            errors={"email": "Este email já está em uso"}
        )
    
    # Criar novo usuário
    user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        nome_completo=body.nome_completo,
        cargo=body.cargo,
        admin=body.admin,
        ativo=body.ativo
    )
    
    db.session.add(user)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(
        data=user.to_dict(),
        message="Usuário criado com sucesso",
        status_code=201
    )

@api_v1.route('/users/<int:id>', methods=['PUT'])
@auth_required()
@validate()
@db_operation
def update_user(id: int, body: UserUpdate):
    """
    Atualiza um usuário existente
    ---
    tags:
      - Usuários
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do usuário
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserUpdate'
    responses:
      200:
        description: Usuário atualizado
      404:
        description: Usuário não encontrado
      400:
        description: Dados inválidos
    """
    # Buscar o usuário pelo ID
    stmt = db.select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    if not user:
        return api_response(message="Usuário não encontrado", status_code=404)
    
    # Verificar se username ou email já existem (se foram alterados)
    if body.username and body.username != user.username:
        username_exists = db.session.execute(
            db.select(User).where(User.username == body.username)
        ).scalar_one_or_none()
        
        if username_exists:
            return api_response(
                message="Nome de usuário já existe",
                status_code=400,
                errors={"username": "Este nome de usuário já está em uso"}
            )
    
    if body.email and body.email != user.email:
        email_exists = db.session.execute(
            db.select(User).where(User.email == body.email)
        ).scalar_one_or_none()
        
        if email_exists:
            return api_response(
                message="Email já existe",
                status_code=400,
                errors={"email": "Este email já está em uso"}
            )
    
    # Atualizar campos
    update_data = body.dict(exclude_unset=True)
    
    # Tratar senha separadamente
    if 'password' in update_data:
        user.password = update_data.pop('password')
    
    # Atualizar outros campos
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(
        data=user.to_dict(),
        message="Usuário atualizado com sucesso"
    )

@api_v1.route('/users/<int:id>', methods=['DELETE'])
@auth_required()
@db_operation
def delete_user(id):
    """
    Remove um usuário
    ---
    tags:
      - Usuários
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do usuário
    responses:
      200:
        description: Usuário removido
      404:
        description: Usuário não encontrado
    """
    # Buscar o usuário pelo ID
    stmt = db.select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    if not user:
        return api_response(message="Usuário não encontrado", status_code=404)
    
    db.session.delete(user)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(message="Usuário removido com sucesso")

# Função para registrar o blueprint na aplicação
def register_api_v1_users(app):
    app.register_blueprint(api_v1)
