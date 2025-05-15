from flask import request, jsonify, g
# Removida a importação de get_current_user de app.auth.middleware
from app.auth.middleware import auth_required 
from sqlalchemy import or_, and_
from datetime import datetime
from app import db
from app.models import Titulo, User, Credor, Devedor # User pode não ser necessário aqui diretamente, mas g.user será do tipo User
from . import titulos

@titulos.route("/")
@auth_required() # Não especifica admin_required, então qualquer usuário autenticado pode acessar
def get_titulos():
    """
    Lista títulos com filtros opcionais
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    parameters:
      - name: numero
        in: query
        type: string
        required: false
        description: Número do título
      - name: protocolo
        in: query
        type: string
        required: false
        description: Protocolo do título
      - name: status
        in: query
        type: string
        required: false
        description: Status do título (Protestado, Pendente, Pago)
      - name: data_inicio
        in: query
        type: string
        required: false
        description: Data inicial (formato YYYY-MM-DD)
      - name: data_fim
        in: query
        type: string
        required: false
        description: Data final (formato YYYY-MM-DD)
      - name: devedor
        in: query
        type: string
        required: false
        description: Nome ou documento do devedor
      - name: page
        in: query
        type: integer
        required: false
        description: Número da página
      - name: per_page
        in: query
        type: integer
        required: false
        description: Itens por página
    responses:
      200:
        description: Lista de títulos
      401:
        description: Não autenticado
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    query = Titulo.query
    
    numero_arg = request.args.get("numero")
    if numero_arg:
        query = query.filter(Titulo.numero.ilike(f"%{numero_arg}%"))
    
    protocolo_arg = request.args.get("protocolo")
    if protocolo_arg:
        query = query.filter(Titulo.protocolo.ilike(f"%{protocolo_arg}%"))
    
    status_arg = request.args.get("status")
    if status_arg:
        query = query.filter(Titulo.status == status_arg)
    
    data_inicio_arg = request.args.get("data_inicio")
    if data_inicio_arg:
        try:
            data_inicio = datetime.strptime(data_inicio_arg, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    data_fim_arg = request.args.get("data_fim")
    if data_fim_arg:
        try:
            data_fim = datetime.strptime(data_fim_arg, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    devedor_arg = request.args.get("devedor")
    if devedor_arg:
        devedores_ids = db.session.query(Devedor.id).filter(
            or_(
                Devedor.nome.ilike(f"%{devedor_arg}%"),
                Devedor.documento.ilike(f"%{devedor_arg}%")
            )
        ).all()
        devedores_ids = [d[0] for d in devedores_ids]
        
        if devedores_ids:
            query = query.filter(Titulo.devedor_id.in_(devedores_ids))
        else:
            return jsonify({
                "items": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "pages": 0
            }), 200
    
    paginated_titulos = query.order_by(Titulo.data_cadastro.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "items": [titulo.to_dict() for titulo in paginated_titulos.items],
        "total": paginated_titulos.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated_titulos.pages
    }), 200

@titulos.route("/<int:id>")
@auth_required()
def get_titulo(id):
    """
    Obtém detalhes de um título específico
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
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
      401:
        description: Não autenticado
    """
    titulo = Titulo.query.get(id)
    
    if not titulo:
        return jsonify({"message": "Título não encontrado"}), 404
    
    titulo_dict = titulo.to_dict()
    
    if titulo.credor:
        titulo_dict["credor"] = titulo.credor.to_dict()
    
    if titulo.devedor:
        titulo_dict["devedor"] = titulo.devedor.to_dict()
    
    if titulo.remessa:
        titulo_dict["remessa"] = {
            "id": titulo.remessa.id,
            "nome_arquivo": titulo.remessa.nome_arquivo,
            "data_envio": titulo.remessa.data_envio.isoformat() if titulo.remessa.data_envio else None,
            "status": titulo.remessa.status
        }
    
    desistencias = []
    for d in titulo.desistencias:
        desistencia = d.to_dict()
        if d.usuario:
            desistencia["usuario"] = {
                "id": d.usuario.id,
                "nome_completo": d.usuario.nome_completo
            }
        desistencias.append(desistencia)
    titulo_dict["desistencias"] = desistencias
    
    erros = []
    for e in titulo.erros:
        erro = e.to_dict()
        erros.append(erro)
    titulo_dict["erros"] = erros
    
    return jsonify(titulo_dict), 200

@titulos.route("/<int:id>/status", methods=["PUT"])
@auth_required() # Por padrão, qualquer usuário autenticado. Se precisar de admin, use @auth_required(admin_required=True)
def update_titulo_status(id):
    """
    Atualiza o status de um título
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título
      - in: body
        name: body
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [Protestado, Pendente, Pago]
            observacao:
              type: string
    responses:
      200:
        description: Status atualizado
      400:
        description: Dados inválidos
      404:
        description: Título não encontrado
      401:
        description: Não autenticado
      403:
        description: Acesso negado (se admin_required fosse True e usuário não fosse admin)
    """
    titulo = Titulo.query.get(id)
    if not titulo:
        return jsonify({"message": "Título não encontrado"}), 404
    
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"message": "Status não informado"}), 400
    
    status = data["status"]
    if status not in ["Protestado", "Pendente", "Pago"]:
        return jsonify({"message": "Status inválido"}), 400
    
    titulo.status = status
    titulo.data_atualizacao = datetime.utcnow()
    
    if status == "Protestado" and not titulo.data_protesto:
        titulo.data_protesto = datetime.utcnow().date()
    
    db.session.commit()
    
    return jsonify({
        "message": "Status atualizado com sucesso",
        "titulo": titulo.to_dict()
    }), 200

@titulos.route("/estatisticas")
@auth_required()
def get_estatisticas():
    """
    Obtém estatísticas dos títulos
    ---
    tags:
      - Títulos
    security:
      - BasicAuth: [] # Atualizado para BasicAuth
    responses:
      200:
        description: Estatísticas dos títulos
      401:
        description: Não autenticado
    """
    total_protestados = Titulo.query.filter_by(status="Protestado").count()
    total_pendentes = Titulo.query.filter_by(status="Pendente").count()
    total_pagos = Titulo.query.filter_by(status="Pago").count()
    total_titulos = Titulo.query.count()
    
    valor_protestados = db.session.query(db.func.sum(Titulo.valor)).filter_by(status="Protestado").scalar() or 0
    valor_pendentes = db.session.query(db.func.sum(Titulo.valor)).filter_by(status="Pendente").scalar() or 0
    valor_pagos = db.session.query(db.func.sum(Titulo.valor)).filter_by(status="Pago").scalar() or 0
    valor_total = db.session.query(db.func.sum(Titulo.valor)).scalar() or 0
    
    return jsonify({
        "total_titulos": total_titulos,
        "por_status": {
            "protestados": total_protestados,
            "pendentes": total_pendentes,
            "pagos": total_pagos
        },
        "valor_total": float(valor_total),
        "valor_por_status": {
            "protestados": float(valor_protestados),
            "pendentes": float(valor_pendentes),
            "pagos": float(valor_pagos)
        }
    }), 200


