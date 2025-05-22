from functools import wraps
from flask import Blueprint, jsonify, request, current_app, g
from flask_pydantic import validate
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime

from app.models import Titulo
from app.auth.middleware import auth_required
from app import db

# Criação do blueprint com versionamento
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Modelos Pydantic para validação
class TituloBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=50)
    protocolo: str = Field(..., min_length=1, max_length=50)
    valor: float = Field(..., gt=0)
    data_emissao: date
    data_vencimento: date
    credor_id: int
    devedor_id: int
    
    @validator('data_vencimento')
    def data_vencimento_must_be_after_emissao(cls, v, values):
        if 'data_emissao' in values and v < values['data_emissao']:
            raise ValueError('Data de vencimento deve ser posterior à data de emissão')
        return v

class TituloCreate(TituloBase):
    especie: Optional[str] = Field(None, max_length=50)
    aceite: bool = False
    nosso_numero: Optional[str] = Field(None, max_length=50)

class TituloUpdate(BaseModel):
    numero: Optional[str] = Field(None, min_length=1, max_length=50)
    protocolo: Optional[str] = Field(None, min_length=1, max_length=50)
    valor: Optional[float] = Field(None, gt=0)
    data_emissao: Optional[date] = None
    data_vencimento: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)
    credor_id: Optional[int] = None
    devedor_id: Optional[int] = None
    especie: Optional[str] = Field(None, max_length=50)
    aceite: Optional[bool] = None
    nosso_numero: Optional[str] = Field(None, max_length=50)

class TituloResponse(TituloBase):
    id: int
    status: str
    remessa_id: Optional[int] = None
    data_protesto: Optional[date] = None
    especie: Optional[str] = None
    aceite: bool
    nosso_numero: Optional[str] = None
    data_cadastro: datetime
    data_atualizacao: datetime

class PaginatedResponse(BaseModel):
    items: List[TituloResponse]
    total: int
    page: int
    per_page: int
    pages: int

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
@api_v1.route('/titulos', methods=['GET'])
@auth_required()
def get_titulos():
    """
    Lista todos os títulos com filtros opcionais e paginação
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: []
    parameters:
      - name: numero
        in: query
        type: string
        required: false
        description: Número do título
      - name: status
        in: query
        type: string
        required: false
        description: Status do título
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
        description: Lista de títulos paginada
    """
    # Obter parâmetros de consulta
    numero = request.args.get('numero')
    status = request.args.get('status')
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Construir a consulta usando SQLAlchemy 2.0
    stmt = db.select(Titulo)
    
    # Aplicar filtros
    if numero:
        stmt = stmt.where(Titulo.numero == numero)
    
    if status:
        stmt = stmt.where(Titulo.status == status)
    
    # Executar a consulta paginada
    pagination = db.paginate(stmt, page=page, per_page=per_page)
    
    # Preparar resposta
    response_data = {
        "items": [titulo.to_dict() for titulo in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }
    
    return api_response(data=response_data)

@api_v1.route('/titulos/<int:id>', methods=['GET'])
@auth_required()
def get_titulo(id):
    """
    Obtém detalhes de um título específico
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título
    responses:
      200:
        description: Detalhes do título
      404:
        description: Título não encontrado
    """
    # Buscar o título pelo ID usando SQLAlchemy 2.0
    stmt = db.select(Titulo).where(Titulo.id == id)
    titulo = db.session.execute(stmt).scalar_one_or_none()
    
    if not titulo:
        return api_response(message="Título não encontrado", status_code=404)
    
    return api_response(data=titulo.to_dict())

@api_v1.route('/titulos', methods=['POST'])
@auth_required()
@validate()
@db_operation
def create_titulo(body: TituloCreate):
    """
    Cria um novo título
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: []
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TituloCreate'
    responses:
      201:
        description: Título criado
      400:
        description: Dados inválidos
    """
    # Criar novo título
    titulo = Titulo(
        numero=body.numero,
        protocolo=body.protocolo,
        valor=body.valor,
        data_emissao=body.data_emissao,
        data_vencimento=body.data_vencimento,
        status="Pendente",
        credor_id=body.credor_id,
        devedor_id=body.devedor_id,
        especie=body.especie,
        aceite=body.aceite,
        nosso_numero=body.nosso_numero
    )
    
    db.session.add(titulo)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(
        data=titulo.to_dict(),
        message="Título criado com sucesso",
        status_code=201
    )

@api_v1.route('/titulos/<int:id>', methods=['PUT'])
@auth_required()
@validate()
@db_operation
def update_titulo(id: int, body: TituloUpdate):
    """
    Atualiza um título existente
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TituloUpdate'
    responses:
      200:
        description: Título atualizado
      404:
        description: Título não encontrado
      400:
        description: Dados inválidos
    """
    # Buscar o título pelo ID
    stmt = db.select(Titulo).where(Titulo.id == id)
    titulo = db.session.execute(stmt).scalar_one_or_none()
    
    if not titulo:
        return api_response(message="Título não encontrado", status_code=404)
    
    # Atualizar campos
    for field, value in body.dict(exclude_unset=True).items():
        setattr(titulo, field, value)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(
        data=titulo.to_dict(),
        message="Título atualizado com sucesso"
    )

@api_v1.route('/titulos/<int:id>', methods=['DELETE'])
@auth_required()
@db_operation
def delete_titulo(id):
    """
    Remove um título
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título
    responses:
      200:
        description: Título removido
      404:
        description: Título não encontrado
    """
    # Buscar o título pelo ID
    stmt = db.select(Titulo).where(Titulo.id == id)
    titulo = db.session.execute(stmt).scalar_one_or_none()
    
    if not titulo:
        return api_response(message="Título não encontrado", status_code=404)
    
    db.session.delete(titulo)
    
    # O commit é feito pelo decorador db_operation
    
    return api_response(message="Título removido com sucesso")

# Função para registrar o blueprint na aplicação
def register_api_v1(app):
    app.register_blueprint(api_v1)
