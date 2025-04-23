from datetime import datetime
from flask import request, jsonify
from app.auth.middleware import auth_required, get_current_user
from sqlalchemy import or_, and_
from app import db
from app.models import Desistencia, Titulo, User
from . import desistencias

@desistencias.route('/', methods=['GET'])
@auth_required()
def get_desistencias():
    """
    Lista solicitações de desistência com filtros opcionais
    ---
    tags:
      - Desistências
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Status da desistência (Aprovada, Pendente, Rejeitada)
      - name: titulo_id
        in: query
        type: integer
        required: false
        description: ID do título
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
        description: Lista de desistências
    """
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Construir query base
    query = Desistencia.query
    
    # Aplicar filtros
    if request.args.get('status'):
        query = query.filter(Desistencia.status == request.args.get('status'))
    
    if request.args.get('titulo_id'):
        query = query.filter(Desistencia.titulo_id == request.args.get('titulo_id'))
    
    # Filtro por data
    if request.args.get('data_inicio'):
        try:
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d')
            query = query.filter(Desistencia.data_solicitacao >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if request.args.get('data_fim'):
        try:
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d')
            # Adicionar 1 dia para incluir todo o dia final
            query = query.filter(Desistencia.data_solicitacao <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query com paginação
    paginated_desistencias = query.order_by(Desistencia.data_solicitacao.desc()).paginate(page=page, per_page=per_page)
    
    # Formatar resposta
    items = []
    for desistencia in paginated_desistencias.items:
        item = desistencia.to_dict()
        
        # Adicionar dados do título
        if desistencia.titulo:
            item['titulo'] = {
                'id': desistencia.titulo.id,
                'numero': desistencia.titulo.numero,
                'protocolo': desistencia.titulo.protocolo,
                'valor': float(desistencia.titulo.valor) if desistencia.titulo.valor else None,
                'status': desistencia.titulo.status
            }
            
            # Adicionar dados do devedor
            if desistencia.titulo.devedor:
                item['devedor'] = {
                    'id': desistencia.titulo.devedor.id,
                    'nome': desistencia.titulo.devedor.nome,
                    'documento': desistencia.titulo.devedor.documento
                }
        
        # Adicionar dados do usuário solicitante
        if desistencia.usuario:
            item['usuario'] = {
                'id': desistencia.usuario.id,
                'nome_completo': desistencia.usuario.nome_completo
            }
        
        items.append(item)
    
    return jsonify({
        'items': items,
        'total': paginated_desistencias.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated_desistencias.pages
    }), 200

@desistencias.route('/<int:id>', methods=['GET'])
@auth_required()
def get_desistencia(id):
    """
    Obtém detalhes de uma solicitação de desistência específica
    ---
    tags:
      - Desistências
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da desistência
    responses:
      200:
        description: Detalhes da desistência
      404:
        description: Desistência não encontrada
    """
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Obter dados relacionados
    desistencia_dict = desistencia.to_dict()
    
    # Adicionar dados do título
    if desistencia.titulo:
        desistencia_dict['titulo'] = desistencia.titulo.to_dict()
        
        # Adicionar dados do devedor
        if desistencia.titulo.devedor:
            desistencia_dict['devedor'] = desistencia.titulo.devedor.to_dict()
        
        # Adicionar dados do credor
        if desistencia.titulo.credor:
            desistencia_dict['credor'] = desistencia.titulo.credor.to_dict()
    
    # Adicionar dados do usuário solicitante
    if desistencia.usuario:
        desistencia_dict['usuario'] = {
            'id': desistencia.usuario.id,
            'nome_completo': desistencia.usuario.nome_completo,
            'email': desistencia.usuario.email
        }
    
    # Adicionar dados do usuário que processou
    if desistencia.usuario_processamento:
        desistencia_dict['usuario_processamento'] = {
            'id': desistencia.usuario_processamento.id,
            'nome_completo': desistencia.usuario_processamento.nome_completo,
            'email': desistencia.usuario_processamento.email
        }
    
    return jsonify(desistencia_dict), 200

@desistencias.route('/', methods=['POST'])
@auth_required()
def create_desistencia():
    """
    Cria uma nova solicitação de desistência
    ---
    tags:
      - Desistências
    security:
      - JWT: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - titulo_id
            - motivo
          properties:
            titulo_id:
              type: integer
            motivo:
              type: string
            observacoes:
              type: string
    responses:
      201:
        description: Desistência criada
      400:
        description: Dados inválidos
      404:
        description: Título não encontrado
    """
    current_user = get_current_user()
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ('titulo_id', 'motivo')):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    # Verificar se o título existe
    titulo = Titulo.query.get(data['titulo_id'])
    if not titulo:
        return jsonify({'message': 'Título não encontrado'}), 404
    
    # Verificar se já existe uma desistência pendente para este título
    desistencia_existente = Desistencia.query.filter_by(
        titulo_id=titulo.id, 
        status='Pendente'
    ).first()
    
    if desistencia_existente:
        return jsonify({
            'message': 'Já existe uma solicitação de desistência pendente para este título',
            'desistencia_id': desistencia_existente.id
        }), 409
    
    # Criar nova desistência
    desistencia = Desistencia(
        titulo_id=titulo.id,
        motivo=data['motivo'],
        observacoes=data.get('observacoes'),
        status='Pendente',
        usuario_id=current_user.id
    )
    
    db.session.add(desistencia)
    db.session.commit()
    
    return jsonify({
        'message': 'Solicitação de desistência criada com sucesso',
        'desistencia': desistencia.to_dict()
    }), 201

@desistencias.route('/<int:id>/processar', methods=['PUT'])
@auth_required()
def processar_desistencia(id):
    """
    Processa uma solicitação de desistência (aprovar ou rejeitar)
    ---
    tags:
      - Desistências
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da desistência
      - in: body
        name: body
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [Aprovada, Rejeitada]
            observacoes:
              type: string
    responses:
      200:
        description: Desistência processada
      400:
        description: Dados inválidos
      403:
        description: Acesso negado
      404:
        description: Desistência não encontrada
    """
    current_user = get_current_user()
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verificar se o usuário tem permissão para processar desistências
    # Em um sistema real, isso seria verificado com base em permissões específicas
    # Para simplificar, vamos assumir que apenas administradores podem processar
    if not current_user.admin:
        return jsonify({'message': 'Acesso negado. Apenas administradores podem processar desistências'}), 403
    
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Verificar se a desistência já foi processada
    if desistencia.status != 'Pendente':
        return jsonify({'message': f'Esta desistência já foi {desistencia.status.lower()}'}), 400
    
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'message': 'Status não informado'}), 400
    
    # Validar status
    status = data['status']
    if status not in ['Aprovada', 'Rejeitada']:
        return jsonify({'message': 'Status inválido. Deve ser Aprovada ou Rejeitada'}), 400
    
    # Atualizar desistência
    desistencia.status = status
    desistencia.data_processamento = datetime.utcnow()
    desistencia.usuario_processamento_id = current_user.id
    
    if 'observacoes' in data and data['observacoes']:
        # Adicionar observações do processamento às observações existentes
        observacoes_atuais = desistencia.observacoes or ''
        desistencia.observacoes = f"{observacoes_atuais}\n\nProcessamento ({datetime.utcnow().strftime('%d/%m/%Y %H:%M')}): {data['observacoes']}"
    
    # Se aprovada, atualizar status do título
    if status == 'Aprovada' and desistencia.titulo:
        desistencia.titulo.status = 'Pago'  # Ou outro status apropriado para títulos com desistência
        desistencia.titulo.data_atualizacao = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Desistência {status.lower()} com sucesso',
        'desistencia': desistencia.to_dict()
    }), 200

@desistencias.route('/estatisticas', methods=['GET'])
@auth_required()
def get_estatisticas():
    """
    Obtém estatísticas das desistências
    ---
    tags:
      - Desistências
    security:
      - JWT: []
    responses:
      200:
        description: Estatísticas das desistências
    """
    # Total de desistências por status
    total_aprovadas = Desistencia.query.filter_by(status='Aprovada').count()
    total_pendentes = Desistencia.query.filter_by(status='Pendente').count()
    total_rejeitadas = Desistencia.query.filter_by(status='Rejeitada').count()
    
    # Total geral
    total_desistencias = total_aprovadas + total_pendentes + total_rejeitadas
    
    # Motivos mais comuns (top 5)
    motivos = db.session.query(
        Desistencia.motivo, 
        db.func.count(Desistencia.id).label('total')
    ).group_by(Desistencia.motivo).order_by(db.func.count(Desistencia.id).desc()).limit(5).all()
    
    return jsonify({
        'total_desistencias': total_desistencias,
        'por_status': {
            'aprovadas': total_aprovadas,
            'pendentes': total_pendentes,
            'rejeitadas': total_rejeitadas
        },
        'motivos_comuns': {motivo: total for motivo, total in motivos}
    }), 200