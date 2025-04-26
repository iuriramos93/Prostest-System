from datetime import datetime
from flask import request, jsonify
from app.auth.middleware import auth_required, get_current_user
from sqlalchemy import or_, and_
from app import db
from app.models import Titulo, User, Credor, Devedor
from . import protestos

@protestos.route('/', methods=['GET'])
@auth_required()
def get_protestos():
    """
    Lista protestos com filtros opcionais
    ---
    tags:
      - Protestos
    security:
      - JWT: []
    parameters:
      - name: numero_titulo
        in: query
        type: string
        required: false
        description: Número do título
      - name: protocolo
        in: query
        type: string
        required: false
        description: Protocolo do título
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
        description: Lista de protestos
    """
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Construir query base - apenas títulos protestados
    query = Titulo.query.filter(Titulo.status == 'Protestado')
    
    # Aplicar filtros
    if request.args.get('numero_titulo'):
        query = query.filter(Titulo.numero.ilike(f'%{request.args.get("numero_titulo")}%'))
    
    if request.args.get('protocolo'):
        query = query.filter(Titulo.protocolo.ilike(f'%{request.args.get("protocolo")}%'))
    
    # Filtro por data de protesto
    if request.args.get('data_inicio'):
        try:
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d').date()
            query = query.filter(Titulo.data_protesto >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if request.args.get('data_fim'):
        try:
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d').date()
            query = query.filter(Titulo.data_protesto <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Filtro por devedor (nome ou documento)
    if request.args.get('devedor'):
        devedor_termo = request.args.get('devedor')
        # Buscar IDs de devedores que correspondem ao termo
        devedores_ids = db.session.query(Devedor.id).filter(
            or_(
                Devedor.nome.ilike(f'%{devedor_termo}%'),
                Devedor.documento.ilike(f'%{devedor_termo}%')
            )
        ).all()
        devedores_ids = [d[0] for d in devedores_ids]
        
        if devedores_ids:
            query = query.filter(Titulo.devedor_id.in_(devedores_ids))
        else:
            # Se não encontrar nenhum devedor, retornar lista vazia
            return jsonify({
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0
            }), 200
    
    # Executar query com paginação
    paginated_protestos = query.order_by(Titulo.data_protesto.desc()).paginate(page=page, per_page=per_page)
    
    # Formatar resposta
    items = []
    for titulo in paginated_protestos.items:
        item = titulo.to_dict()
        
        # Adicionar dados do devedor
        if titulo.devedor:
            item['devedor'] = titulo.devedor.to_dict()
        
        # Adicionar dados do credor
        if titulo.credor:
            item['credor'] = titulo.credor.to_dict()
            
        items.append(item)
    
    return jsonify({
        'items': items,
        'total': paginated_protestos.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated_protestos.pages
    }), 200

@protestos.route('/<int:id>', methods=['GET'])
@auth_required()
def get_protesto(id):
    """
    Obtém detalhes de um protesto específico
    ---
    tags:
      - Protestos
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título protestado
    responses:
      200:
        description: Detalhes do protesto
      404:
        description: Protesto não encontrado
    """
    titulo = Titulo.query.get(id)
    
    if not titulo:
        return jsonify({'message': 'Título não encontrado'}), 404
    
    if titulo.status != 'Protestado':
        return jsonify({'message': 'Este título não está protestado'}), 400
    
    # Obter dados relacionados
    titulo_dict = titulo.to_dict()
    
    # Adicionar dados do credor
    if titulo.credor:
        titulo_dict['credor'] = titulo.credor.to_dict()
    
    # Adicionar dados do devedor
    if titulo.devedor:
        titulo_dict['devedor'] = titulo.devedor.to_dict()
    
    # Adicionar dados da remessa
    if titulo.remessa:
        titulo_dict['remessa'] = {
            'id': titulo.remessa.id,
            'nome_arquivo': titulo.remessa.nome_arquivo,
            'data_envio': titulo.remessa.data_envio.isoformat() if titulo.remessa.data_envio else None,
            'status': titulo.remessa.status
        }
    
    return jsonify(titulo_dict), 200

@protestos.route('/registrar', methods=['POST'])
@auth_required()
def registrar_protesto():
    """
    Registra um protesto para um título
    ---
    tags:
      - Protestos
    security:
      - JWT: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - titulo_id
            - data_protesto
          properties:
            titulo_id:
              type: integer
            data_protesto:
              type: string
              format: date
            observacoes:
              type: string
    responses:
      200:
        description: Protesto registrado com sucesso
      400:
        description: Dados inválidos
      404:
        description: Título não encontrado
    """
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ('titulo_id', 'data_protesto')):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    # Validar formato da data
    try:
        data_protesto = datetime.strptime(data['data_protesto'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Buscar título
    titulo = Titulo.query.get(data['titulo_id'])
    
    if not titulo:
        return jsonify({'message': 'Título não encontrado'}), 404
    
    # Verificar se o título já está protestado
    if titulo.status == 'Protestado':
        return jsonify({'message': 'Título já está protestado'}), 400
    
    # Atualizar status e data de protesto
    titulo.status = 'Protestado'
    titulo.data_protesto = data_protesto
    
    # Registrar observações se fornecidas
    if 'observacoes' in data and data['observacoes']:
        # Aqui poderia ser implementado um registro de observações em uma tabela separada
        pass
    
    db.session.commit()
    
    return jsonify({
        'message': 'Protesto registrado com sucesso',
        'titulo': titulo.to_dict()
    }), 200

@protestos.route('/cancelar/<int:id>', methods=['POST'])
@auth_required()
def cancelar_protesto(id):
    """
    Cancela um protesto
    ---
    tags:
      - Protestos
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do título protestado
      - in: body
        name: body
        schema:
          type: object
          required:
            - motivo
          properties:
            motivo:
              type: string
            observacoes:
              type: string
    responses:
      200:
        description: Protesto cancelado com sucesso
      400:
        description: Dados inválidos
      404:
        description: Protesto não encontrado
    """
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    # Verificar se o usuário tem permissão para cancelar protestos
    if not current_user.admin:
        return jsonify({'message': 'Sem permissão para cancelar protestos'}), 403
    
    data = request.get_json()
    
    if not data or 'motivo' not in data:
        return jsonify({'message': 'Motivo do cancelamento é obrigatório'}), 400
    
    # Buscar título
    titulo = Titulo.query.get(id)
    
    if not titulo:
        return jsonify({'message': 'Título não encontrado'}), 404
    
    # Verificar se o título está protestado
    if titulo.status != 'Protestado':
        return jsonify({'message': 'Este título não está protestado'}), 400
    
    # Atualizar status e remover data de protesto
    titulo.status = 'Pendente'  # ou outro status apropriado
    titulo.data_protesto = None
    
    # Registrar o cancelamento (poderia ser em uma tabela separada)
    # Exemplo: criar um registro de histórico
    
    db.session.commit()
    
    return jsonify({
        'message': 'Protesto cancelado com sucesso',
        'titulo': titulo.to_dict()
    }), 200

@protestos.route('/dashboard', methods=['GET'])
@auth_required()
def dashboard_protestos():
    """
    Retorna estatísticas sobre protestos
    ---
    tags:
      - Protestos
    security:
      - JWT: []
    responses:
      200:
        description: Estatísticas de protestos
    """
    # Total de protestos
    total_protestos = Titulo.query.filter(Titulo.status == 'Protestado').count()
    
    # Protestos por mês (últimos 6 meses)
    hoje = datetime.utcnow().date()
    seis_meses_atras = hoje.replace(month=hoje.month - 6 if hoje.month > 6 else hoje.month + 6, 
                                  year=hoje.year if hoje.month > 6 else hoje.year - 1)
    
    protestos_por_mes = db.session.query(
        db.func.date_trunc('month', Titulo.data_protesto).label('mes'),
        db.func.count().label('total')
    ).filter(
        Titulo.status == 'Protestado',
        Titulo.data_protesto >= seis_meses_atras
    ).group_by('mes').order_by('mes').all()
    
    # Formatar resultado
    meses_protestos = [{
        'mes': item[0].strftime('%Y-%m'),
        'total': item[1]
    } for item in protestos_por_mes]
    
    # Valor total de protestos
    valor_total = db.session.query(db.func.sum(Titulo.valor)).filter(
        Titulo.status == 'Protestado'
    ).scalar()
    
    return jsonify({
        'total_protestos': total_protestos,
        'protestos_por_mes': meses_protestos,
        'valor_total': float(valor_total) if valor_total else 0
    }), 200