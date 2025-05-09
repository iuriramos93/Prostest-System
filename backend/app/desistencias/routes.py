from datetime import datetime
from flask import request, jsonify, current_app
from app.auth.middleware import auth_required, get_current_user
from sqlalchemy import or_, and_
from app import db
from app.models import Desistencia, Titulo, User, Devedor, Erro
from . import desistencias

@desistencias.route('/', methods=['GET'])
@auth_required()
def get_desistencias():
    """
    Lista todas as desistências com filtros opcionais
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
      - name: dataInicio
        in: query
        type: string
        required: false
        description: Data de início (formato YYYY-MM-DD)
      - name: dataFim
        in: query
        type: string
        required: false
        description: Data de fim (formato YYYY-MM-DD)
    responses:
      200:
        description: Lista de desistências
    """
    # Obter parâmetros de consulta
    status = request.args.get('status')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
    # Construir a consulta
    query = Desistencia.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Desistencia.status == status)
    
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Desistencia.data_solicitacao >= data_inicio_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataInicio. Use YYYY-MM-DD'}), 400
    
    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Desistencia.data_solicitacao <= data_fim_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataFim. Use YYYY-MM-DD'}), 400
    
    # Ordenar por data de solicitação (mais recentes primeiro)
    query = query.order_by(Desistencia.data_solicitacao.desc())
    
    # Executar a consulta
    desistencias_list = query.all()
    
    # Retornar os resultados
    return jsonify([desistencia.to_dict() for desistencia in desistencias_list]), 200

@desistencias.route('/<int:id>', methods=['GET'])
@auth_required()
def get_desistencia(id):
    """
    Obtém detalhes de uma desistência específica
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
    # Buscar a desistência pelo ID
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Buscar título associado à desistência
    titulo = Titulo.query.get(desistencia.titulo_id)
    
    # Preparar resposta
    response = desistencia.to_dict()
    if titulo:
        response['titulo'] = titulo.to_dict()
    
    return jsonify(response), 200

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
            - numeroTitulo
            - protocolo
            - devedor
            - valor
            - motivo
          properties:
            numeroTitulo:
              type: string
            protocolo:
              type: string
            devedor:
              type: string
            valor:
              type: number
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
    
    if not data or not all(k in data for k in ('numeroTitulo', 'protocolo', 'devedor', 'valor', 'motivo')):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    # Verificar se o título existe pelo número e protocolo
    titulo = Titulo.query.filter_by(numero=data['numeroTitulo'], protocolo=data['protocolo']).first()
    
    if not titulo:
        # Se não encontrar, criar um novo título
        devedor = Devedor.query.filter_by(nome=data['devedor']).first()
        
        if not devedor:
            devedor = Devedor(nome=data['devedor'])
            db.session.add(devedor)
            db.session.flush()
        
        titulo = Titulo(
            numero=data['numeroTitulo'],
            protocolo=data['protocolo'],
            valor=data['valor'],
            devedor_id=devedor.id,
            status='Protestado'
        )
        db.session.add(titulo)
        db.session.flush()
    
    # Verificar se já existe uma desistência pendente para este título
    desistencia_existente = Desistencia.query.filter_by(
        titulo_id=titulo.id, 
        status='Pendente'
    ).first()
    
    if desistencia_existente:
        return jsonify({
            'message': 'Já existe uma solicitação de desistência pendente para este título',
            'id': str(desistencia_existente.id)
        }), 409
    
    # Criar nova desistência
    desistencia = Desistencia(
        titulo_id=titulo.id,
        motivo=data['motivo'],
        observacoes=data.get('observacoes'),
        status='Pendente',
        usuario_id=current_user.id,
        data_solicitacao=datetime.utcnow()
    )
    
    db.session.add(desistencia)
    db.session.commit()
    
    return jsonify({
        'message': 'Solicitação de desistência criada com sucesso',
        'id': str(desistencia.id),
        'numeroTitulo': titulo.numero,
        'protocolo': titulo.protocolo,
        'devedor': data['devedor'],
        'valor': float(titulo.valor) if titulo.valor else float(data['valor']),
        'dataSolicitacao': desistencia.data_solicitacao.isoformat(),
        'motivo': desistencia.motivo,
        'observacoes': desistencia.observacoes,
        'status': 'PENDENTE'
    }), 201

@desistencias.route('/<int:id>', methods=['PUT'])
@auth_required()
def update_desistencia(id):
    """
    Atualiza uma solicitação de desistência existente
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
          properties:
            numeroTitulo:
              type: string
            protocolo:
              type: string
            devedor:
              type: string
            valor:
              type: number
            motivo:
              type: string
            observacoes:
              type: string
    responses:
      200:
        description: Desistência atualizada
      400:
        description: Dados inválidos
      404:
        description: Desistência não encontrada
    """
    current_user = get_current_user()
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Verificar se a desistência já foi processada
    if desistencia.status != 'Pendente':
        return jsonify({'message': f'Esta desistência já foi {desistencia.status.lower()} e não pode ser editada'}), 400
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Dados não fornecidos'}), 400
    
    # Atualizar campos da desistência
    if 'motivo' in data:
        desistencia.motivo = data['motivo']
    
    if 'observacoes' in data:
        desistencia.observacoes = data['observacoes']
    
    # Atualizar dados do título associado
    if desistencia.titulo:
        titulo = desistencia.titulo
        
        if 'numeroTitulo' in data:
            titulo.numero = data['numeroTitulo']
        
        if 'protocolo' in data:
            titulo.protocolo = data['protocolo']
        
        if 'valor' in data:
            titulo.valor = data['valor']
        
        if 'devedor' in data and titulo.devedor:
            titulo.devedor.nome = data['devedor']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Desistência atualizada com sucesso',
        'id': str(desistencia.id),
        'numeroTitulo': desistencia.titulo.numero if desistencia.titulo else '',
        'protocolo': desistencia.titulo.protocolo if desistencia.titulo else '',
        'devedor': desistencia.titulo.devedor.nome if desistencia.titulo and desistencia.titulo.devedor else '',
        'valor': float(desistencia.titulo.valor) if desistencia.titulo and desistencia.titulo.valor else 0,
        'dataSolicitacao': desistencia.data_solicitacao.isoformat() if desistencia.data_solicitacao else None,
        'motivo': desistencia.motivo,
        'observacoes': desistencia.observacoes,
        'status': desistencia.status.upper() if desistencia.status else 'PENDENTE'
    }), 200

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
        'id': str(desistencia.id),
        'numeroTitulo': desistencia.titulo.numero if desistencia.titulo else '',
        'protocolo': desistencia.titulo.protocolo if desistencia.titulo else '',
        'devedor': desistencia.titulo.devedor.nome if desistencia.titulo and desistencia.titulo.devedor else '',
        'valor': float(desistencia.titulo.valor) if desistencia.titulo and desistencia.titulo.valor else 0,
        'dataSolicitacao': desistencia.data_solicitacao.isoformat() if desistencia.data_solicitacao else None,
        'motivo': desistencia.motivo,
        'observacoes': desistencia.observacoes,
        'status': status.upper()
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

@desistencias.route('/<int:id>/aprovar', methods=['PUT'])
@auth_required()
def aprovar_desistencia(id):
    """
    Aprova uma desistência
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
        description: Desistência aprovada
      404:
        description: Desistência não encontrada
      400:
        description: Desistência não pode ser aprovada
    """
    # Buscar a desistência pelo ID
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Verificar se a desistência já foi processada
    if desistencia.status != 'Pendente':
        return jsonify({'message': f'Desistência não pode ser aprovada. Status atual: {desistencia.status}'}), 400
    
    current_user = get_current_user()
    
    # Atualizar a desistência
    desistencia.status = 'Aprovada'
    desistencia.data_processamento = datetime.utcnow()
    desistencia.usuario_processamento_id = current_user.id if current_user else None
    
    # Atualizar o título associado
    titulo = Titulo.query.get(desistencia.titulo_id)
    if titulo:
        titulo.status = 'Desistido'
    
    db.session.commit()
    
    return jsonify({'message': 'Desistência aprovada com sucesso', 'desistencia': desistencia.to_dict()}), 200

@desistencias.route('/<int:id>/rejeitar', methods=['PUT'])
@auth_required()
def rejeitar_desistencia(id):
    """
    Rejeita uma desistência
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
          properties:
            motivo:
              type: string
              description: Motivo da rejeição
    responses:
      200:
        description: Desistência rejeitada
      404:
        description: Desistência não encontrada
      400:
        description: Desistência não pode ser rejeitada
    """
    # Buscar a desistência pelo ID
    desistencia = Desistencia.query.get(id)
    
    if not desistencia:
        return jsonify({'message': 'Desistência não encontrada'}), 404
    
    # Verificar se a desistência já foi processada
    if desistencia.status != 'Pendente':
        return jsonify({'message': f'Desistência não pode ser rejeitada. Status atual: {desistencia.status}'}), 400
    
    # Obter dados da requisição
    data = request.get_json()
    motivo = data.get('motivo') if data else None
    
    current_user = get_current_user()
    
    # Atualizar a desistência
    desistencia.status = 'Rejeitada'
    desistencia.data_processamento = datetime.utcnow()
    desistencia.usuario_processamento_id = current_user.id if current_user else None
    
    if motivo:
        desistencia.observacoes = motivo
    
    db.session.commit()
    
    return jsonify({'message': 'Desistência rejeitada com sucesso', 'desistencia': desistencia.to_dict()}), 200