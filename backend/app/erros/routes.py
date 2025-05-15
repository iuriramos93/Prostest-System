from datetime import datetime
from flask import request, jsonify, g
from app.auth.middleware import auth_required
from sqlalchemy import or_, and_
from app import db
from app.models import Erro, Remessa, Titulo, User
from . import erros

@erros.route("/", methods=["GET"])
@auth_required()
def get_erros():
    """
    Lista erros com filtros opcionais
    ---
    tags:
      - Erros
    security:
      - JWT: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de erro (Validação, Processamento, Sistema)
      - name: remessa_id
        in: query
        type: integer
        required: false
        description: ID da remessa
      - name: titulo_id
        in: query
        type: integer
        required: false
        description: ID do título
      - name: resolvido
        in: query
        type: boolean
        required: false
        description: Status de resolução (true/false)
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
        description: Lista de erros
    """
    # Parâmetros de paginação
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    # Construir query base
    query = Erro.query
    
    # Aplicar filtros
    if request.args.get("tipo"):
        query = query.filter(Erro.tipo == request.args.get("tipo"))
    
    if request.args.get("remessa_id"):
        query = query.filter(Erro.remessa_id == request.args.get("remessa_id"))
    
    if request.args.get("titulo_id"):
        query = query.filter(Erro.titulo_id == request.args.get("titulo_id"))
    
    if request.args.get("resolvido") is not None:
        resolvido = request.args.get("resolvido").lower() == "true"
        query = query.filter(Erro.resolvido == resolvido)
    
    # Filtro por data
    if request.args.get("data_inicio"):
        try:
            data_inicio = datetime.strptime(request.args.get("data_inicio"), "%Y-%m-%d")
            query = query.filter(Erro.data_ocorrencia >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if request.args.get("data_fim"):
        try:
            data_fim = datetime.strptime(request.args.get("data_fim"), "%Y-%m-%d")
            # Adicionar 1 dia para incluir todo o dia final
            query = query.filter(Erro.data_ocorrencia <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Executar query com paginação
    paginated_erros = query.order_by(Erro.data_ocorrencia.desc()).paginate(page=page, per_page=per_page)
    
    # Formatar resposta
    items = []
    for erro in paginated_erros.items:
        item = erro.to_dict()
        
        # Adicionar dados da remessa
        if erro.remessa:
            item["remessa"] = {
                "id": erro.remessa.id,
                "nome_arquivo": erro.remessa.nome_arquivo,
                "data_envio": erro.remessa.data_envio.isoformat() if erro.remessa.data_envio else None,
                "status": erro.remessa.status
            }
        
        # Adicionar dados do título
        if erro.titulo:
            item["titulo"] = {
                "id": erro.titulo.id,
                "numero": erro.titulo.numero,
                "protocolo": erro.titulo.protocolo,
                "valor": float(erro.titulo.valor) if erro.titulo.valor else None,
                "status": erro.titulo.status
            }
        
        # Adicionar dados do usuário que resolveu
        if erro.usuario_resolucao:
            item["usuario_resolucao"] = {
                "id": erro.usuario_resolucao.id,
                "nome_completo": erro.usuario_resolucao.nome_completo
            }
        
        items.append(item)
    
    return jsonify({
        "items": items,
        "total": paginated_erros.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated_erros.pages
    }), 200

@erros.route("/<int:id>", methods=["GET"])
@auth_required()
def get_erro(id):
    """
    Obtém detalhes de um erro específico
    ---
    tags:
      - Erros
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do erro
    responses:
      200:
        description: Detalhes do erro
      404:
        description: Erro não encontrado
    """
    erro = Erro.query.get(id)
    
    if not erro:
        return jsonify({"message": "Erro não encontrado"}), 404
    
    # Obter dados relacionados
    erro_dict = erro.to_dict()
    
    # Adicionar dados da remessa
    if erro.remessa:
        erro_dict["remessa"] = erro.remessa.to_dict()
    
    # Adicionar dados do título
    if erro.titulo:
        erro_dict["titulo"] = erro.titulo.to_dict()
        
        # Adicionar dados do devedor
        if erro.titulo.devedor:
            erro_dict["devedor"] = erro.titulo.devedor.to_dict()
    
    # Adicionar dados do usuário que resolveu
    if erro.usuario_resolucao:
        erro_dict["usuario_resolucao"] = {
            "id": erro.usuario_resolucao.id,
            "nome_completo": erro.usuario_resolucao.nome_completo,
            "email": erro.usuario_resolucao.email
        }
    
    return jsonify(erro_dict), 200

@erros.route("/<int:id>/resolver", methods=["PUT"])
@auth_required()
def resolver_erro(id):
    """
    Marca um erro como resolvido
    ---
    tags:
      - Erros
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do erro
      - in: body
        name: body
        schema:
          type: object
          properties:
            observacao:
              type: string
    responses:
      200:
        description: Erro resolvido
      404:
        description: Erro não encontrado
    """
    current_user = g.user
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({"message": "Usuário não encontrado"}), 404
    
    erro = Erro.query.get(id)
    
    if not erro:
        return jsonify({"message": "Erro não encontrado"}), 404
    
    # Verificar se o erro já foi resolvido
    if erro.resolvido:
        return jsonify({"message": "Este erro já foi resolvido"}), 400
    
    data = request.get_json() or {}
    
    # Atualizar erro
    erro.resolvido = True
    erro.data_resolucao = datetime.utcnow()
    erro.usuario_resolucao_id = current_user.id
    
    # Adicionar observação à mensagem de erro
    if "observacao" in data and data["observacao"]:
        erro.mensagem = f"{erro.mensagem}\n\nResolução ({datetime.utcnow().strftime('%d/%m/%Y %H:%M')}): {data['observacao']}"
    
    db.session.commit()
    
    # Verificar se todos os erros da remessa foram resolvidos
    if erro.remessa_id:
        erros_pendentes = Erro.query.filter_by(remessa_id=erro.remessa_id, resolvido=False).count()
        
        # Se não houver mais erros pendentes e a remessa estiver com status de erro, atualizar para processado
        if erros_pendentes == 0:
            remessa = Remessa.query.get(erro.remessa_id)
            if remessa and remessa.status == "Erro":
                remessa.status = "Processado"
                remessa.data_processamento = datetime.utcnow()
                db.session.commit()
    
    return jsonify({
        "message": "Erro marcado como resolvido",
        "erro": erro.to_dict()
    }), 200

@erros.route("/estatisticas", methods=["GET"])
@auth_required()
def get_estatisticas():
    """
    Obtém estatísticas dos erros
    ---
    tags:
      - Erros
    security:
      - JWT: []
    responses:
      200:
        description: Estatísticas dos erros
    """
    # Total de erros por tipo
    total_validacao = Erro.query.filter_by(tipo="Validação").count()
    total_processamento = Erro.query.filter_by(tipo="Processamento").count()
    total_sistema = Erro.query.filter_by(tipo="Sistema").count()
    
    # Total por status de resolução
    total_resolvidos = Erro.query.filter_by(resolvido=True).count()
    total_pendentes = Erro.query.filter_by(resolvido=False).count()
    
    # Total geral
    total_erros = total_resolvidos + total_pendentes
    
    # Erros por remessa (top 5)
    erros_por_remessa = db.session.query(
        Erro.remessa_id, 
        Remessa.nome_arquivo,
        db.func.count(Erro.id).label("total")
    ).join(Remessa, Erro.remessa_id == Remessa.id)\
    .group_by(Erro.remessa_id, Remessa.nome_arquivo)\
    .order_by(db.func.count(Erro.id).desc())\
    .limit(5).all()
    
    return jsonify({
        "total_erros": total_erros,
        "por_tipo": {
            "validacao": total_validacao,
            "processamento": total_processamento,
            "sistema": total_sistema
        },
        "por_status": {
            "resolvidos": total_resolvidos,
            "pendentes": total_pendentes
        },
        "por_remessa": [{
            "remessa_id": remessa_id,
            "nome_arquivo": nome_arquivo,
            "total": total
        } for remessa_id, nome_arquivo, total in erros_por_remessa]
    }), 200

@erros.route("/", methods=["POST"])
@auth_required()
def create_erro():
    """
    Cria um novo registro de erro
    ---
    tags:
      - Erros
    security:
      - JWT: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - tipo
            - mensagem
          properties:
            remessa_id:
              type: integer
              description: ID da remessa relacionada ao erro
            titulo_id:
              type: integer
              description: ID do título relacionado ao erro
            tipo:
              type: string
              description: Tipo de erro (Validação, Processamento, Sistema)
              enum: [Validação, Processamento, Sistema]
            mensagem:
              type: string
              description: Mensagem detalhada do erro
    responses:
      201:
        description: Erro criado com sucesso
      400:
        description: Dados inválidos
      404:
        description: Remessa ou título não encontrado
    """
    data = request.get_json() or {}
    
    # Validar campos obrigatórios
    if "tipo" not in data or "mensagem" not in data:
        return jsonify({"message": "Os campos tipo e mensagem são obrigatórios"}), 400
    
    # Validar tipo de erro
    tipos_validos = ["Validação", "Processamento", "Sistema"]
    if data["tipo"] not in tipos_validos:
        return jsonify({"message": f"Tipo de erro inválido. Valores aceitos: {', '.join(tipos_validos)}"}), 400
    
    # Verificar se a remessa existe, se fornecida
    if "remessa_id" in data and data["remessa_id"]:
        remessa = Remessa.query.get(data["remessa_id"])
        if not remessa:
            return jsonify({"message": "Remessa não encontrada"}), 404
    
    # Verificar se o título existe, se fornecido
    if "titulo_id" in data and data["titulo_id"]:
        titulo = Titulo.query.get(data["titulo_id"])
        if not titulo:
            return jsonify({"message": "Título não encontrado"}), 404
    
    # Criar novo erro
    novo_erro = Erro(
        remessa_id=data.get("remessa_id"),
        titulo_id=data.get("titulo_id"),
        tipo=data["tipo"],
        mensagem=data["mensagem"],
        data_ocorrencia=datetime.utcnow(),
        resolvido=False
    )
    
    # Atualizar status da remessa para "Erro" se fornecida
    if "remessa_id" in data and data["remessa_id"]:
        remessa = Remessa.query.get(data["remessa_id"])
        if remessa and remessa.status != "Erro":
            remessa.status = "Erro"
            db.session.add(remessa)
    
    db.session.add(novo_erro)
    db.session.commit()
    
    return jsonify({
        "message": "Erro registrado com sucesso",
        "erro": novo_erro.to_dict()
    }), 201

