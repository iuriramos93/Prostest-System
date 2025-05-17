import os
import uuid
from datetime import datetime
import xmltodict
from flask import request, jsonify, current_app, g
from app.auth.middleware import auth_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from app import db
from app.models import Remessa, Titulo, User, Credor, Devedor, Erro
from . import remessas

# Função auxiliar para verificar se o arquivo é permitido
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xml'}

@remessas.route('/upload', methods=['POST'])
@auth_required()
def upload_remessa():
    """
    Faz upload de um arquivo de remessa
    ---
    tags:
      - Remessas
    security:
      - BasicAuth: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Arquivo XML de remessa
      - in: formData
        name: uf
        type: string
        required: true
        description: UF do cartório
      - in: formData
        name: tipo
        type: string
        required: true
        description: Tipo de remessa (Remessa ou Desistência)
    responses:
      201:
        description: Arquivo enviado com sucesso
      400:
        description: Arquivo inválido
      415:
        description: Tipo de arquivo não suportado
    """
    current_user = g.user
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verificar se o arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    # Verificar se o arquivo tem nome
    if file.filename == '':
        return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
    
    # Verificar se o arquivo é do tipo permitido
    if not allowed_file(file.filename):
        return jsonify({'message': 'Tipo de arquivo não permitido. Apenas XML é aceito'}), 415
    
    # Verificar se UF e tipo foram informados
    uf = request.form.get('uf')
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    
    if not uf or not tipo:
        return jsonify({'message': 'UF e tipo são obrigatórios'}), 400
    
    if tipo not in ['Remessa', 'Desistência']:
        return jsonify({'message': 'Tipo inválido. Deve ser Remessa ou Desistência'}), 400
    
    # Gerar nome único para o arquivo
    filename = secure_filename(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    
    # Criar diretório de upload se não existir
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Salvar arquivo
    file.save(file_path)
    
    # Criar registro de remessa no banco
    remessa = Remessa(
        nome_arquivo=filename,
        status='Pendente',
        uf=uf,
        tipo=tipo,
        usuario_id=current_user.id
    )
    
    # Adicionar descrição se fornecida
    if descricao:
        remessa.descricao = descricao
    
    db.session.add(remessa)
    db.session.commit()
    
    # Iniciar processamento assíncrono usando o sistema de filas
    try:
        from app.utils.async_tasks import enqueue_task
        
        # Enfileira a tarefa de processamento
        task_id = enqueue_task(
            processar_remessa,
            f"Processamento da remessa {remessa.id}",
            remessa.id, 
            file_path
        )
        
        # Atualiza a remessa com o ID da tarefa
        remessa.task_id = task_id
        db.session.commit()
        
        return jsonify({
            'message': 'Arquivo enviado com sucesso. O processamento foi iniciado em segundo plano.',
            'remessa': remessa.to_dict(),
            'id': remessa.id
        }), 201
    except Exception as e:
        # Registrar erro
        erro = Erro(
            remessa_id=remessa.id,
            tipo='Processamento',
            mensagem=str(e),
            data_ocorrencia=datetime.utcnow()
        )
        db.session.add(erro)
        
        # Atualizar status da remessa
        remessa.status = 'Erro'
        db.session.commit()
        
        return jsonify({
            'message': 'Erro ao processar remessa: ' + str(e),
            'remessa': remessa.to_dict()
        }), 500

# Rota para enviar uma nova desistência
@remessas.route('/desistencias', methods=['POST'])
@auth_required()
def upload_desistencia():
    """
    Faz upload de um arquivo de desistência
    ---
    tags:
      - Desistências
    security:
      - BasicAuth: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Arquivo XML de desistência
      - in: formData
        name: uf
        type: string
        required: true
        description: UF do cartório
      - in: formData
        name: descricao
        type: string
        required: false
        description: Descrição da desistência
    responses:
      201:
        description: Arquivo enviado com sucesso
      400:
        description: Arquivo inválido
      415:
        description: Tipo de arquivo não suportado
    """
    current_user = g.user
    user_id = current_user.id if current_user else None
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Verificar se o arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    # Verificar se o arquivo tem nome
    if file.filename == '':
        return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
    
    # Verificar se o arquivo é do tipo permitido
    if not allowed_file(file.filename):
        return jsonify({'message': 'Tipo de arquivo não permitido. Apenas XML é aceito'}), 415
    
    # Verificar se UF foi informada
    uf = request.form.get('uf')
    descricao = request.form.get('descricao')
    
    if not uf:
        return jsonify({'message': 'UF é obrigatória'}), 400
    
    # Gerar nome único para o arquivo
    filename = secure_filename(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    
    # Criar diretório de upload se não existir
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Salvar arquivo
    file.save(file_path)
    
    # Criar registro de remessa do tipo desistência no banco
    remessa = Remessa(
        nome_arquivo=filename,
        status='Pendente',
        uf=uf,
        tipo='Desistência',
        usuario_id=current_user.id
    )
    
    # Adicionar descrição se fornecida
    if descricao:
        remessa.descricao = descricao
    
    db.session.add(remessa)
    db.session.commit()
    
    # Iniciar processamento assíncrono usando o sistema de filas
    try:
        from app.utils.async_tasks import enqueue_task
        
        # Enfileira a tarefa de processamento
        task_id = enqueue_task(
            processar_desistencia,
            f"Processamento da desistência {remessa.id}",
            remessa.id, 
            file_path
        )
        
        # Atualiza a remessa com o ID da tarefa
        remessa.task_id = task_id
        db.session.commit()
        
        return jsonify({
            'message': 'Desistência enviada com sucesso. O processamento foi iniciado em segundo plano.',
            'remessa': remessa.to_dict(),
            'id': remessa.id
        }), 201
    except Exception as e:
        # Registrar erro
        erro = Erro(
            remessa_id=remessa.id,
            tipo='Processamento',
            mensagem=str(e),
            data_ocorrencia=datetime.utcnow()
        )
        db.session.add(erro)
        
        # Atualizar status da remessa
        remessa.status = 'Erro'
        db.session.commit()
        
        return jsonify({
            'message': 'Erro ao processar desistência: ' + str(e),
            'remessa': remessa.to_dict()
        }), 500

# Função para processar desistência
def processar_desistencia(remessa_id, file_path):
    """
    Processa um arquivo de desistência
    """
    remessa = Remessa.query.get(remessa_id)
    
    if not remessa:
        raise Exception('Remessa não encontrada')
    
    try:
        # Ler arquivo XML
        with open(file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # Converter XML para dicionário
        data = xmltodict.parse(xml_content)
        
        # Implementação específica para desistências...
        # Código para processar o XML de desistência
        
        # Atualizar status da remessa
        remessa.status = 'Processado'
        remessa.data_processamento = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        # Registrar erro
        erro = Erro(
            remessa_id=remessa.id,
            tipo='Processamento',
            mensagem=str(e),
            data_ocorrencia=datetime.utcnow()
        )
        db.session.add(erro)
        
        # Atualizar status da remessa
        remessa.status = 'Erro'
        db.session.commit()
        
        raise e

# Rota para listar remessas com paginação
@remessas.route('/', methods=['GET'])
@auth_required()
def get_remessas():
    """
    Lista todas as remessas com filtros opcionais e paginação
    ---
    tags:
      - Remessas
    security:
      - BasicAuth: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de remessa
      - name: uf
        in: query
        type: string
        required: false
        description: UF do cartório
      - name: status
        in: query
        type: string
        required: false
        description: Status da remessa
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
        description: Lista de remessas paginada
    """
    # Obter parâmetros de consulta
    tipo = request.args.get('tipo')
    uf = request.args.get('uf')
    status = request.args.get('status')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validar parâmetros de paginação
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limitar para evitar sobrecarga
        per_page = 10
    
    # Construir a consulta
    query = Remessa.query
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Remessa.tipo == tipo)
    
    if uf:
        query = query.filter(Remessa.uf == uf)
    
    if status:
        query = query.filter(Remessa.status == status)
    
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio >= data_inicio_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataInicio. Use YYYY-MM-DD'}), 400
    
    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio <= data_fim_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataFim. Use YYYY-MM-DD'}), 400
    
    # Ordenar por data de envio (mais recentes primeiro)
    query = query.order_by(Remessa.data_envio.desc())
    
    # Executar a consulta paginada
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    remessas = pagination.items
    
    # Preparar metadados de paginação
    meta = {
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_page': pagination.next_num if pagination.has_next else None,
        'prev_page': pagination.prev_num if pagination.has_prev else None
    }
    
    # Retornar os resultados com metadados de paginação
    return jsonify({
        'items': [remessa.to_dict() for remessa in remessas],
        'meta': meta
    }), 200

# Rota para obter detalhes de uma remessa
@remessas.route('/<int:id>', methods=['GET'])
@auth_required()
def get_remessa(id):
    """
    Obtém detalhes de uma remessa específica
    ---
    tags:
      - Remessas
    security:
      - BasicAuth: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da remessa
    responses:
      200:
        description: Detalhes da remessa
      404:
        description: Remessa não encontrada
    """
    # Buscar a remessa pelo ID
    remessa = Remessa.query.get(id)
    
    if not remessa:
        return jsonify({'message': 'Remessa não encontrada'}), 404
    
    # Buscar títulos associados à remessa com paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Validar parâmetros de paginação
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    # Consulta paginada de títulos
    titulos_pagination = Titulo.query.filter_by(remessa_id=id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Preparar metadados de paginação para títulos
    titulos_meta = {
        'page': page,
        'per_page': per_page,
        'total': titulos_pagination.total,
        'pages': titulos_pagination.pages,
        'has_next': titulos_pagination.has_next,
        'has_prev': titulos_pagination.has_prev
    }
    
    # Preparar resposta
    response = remessa.to_dict()
    response['titulos'] = {
        'items': [titulo.to_dict() for titulo in titulos_pagination.items],
        'meta': titulos_meta
    }
    
    return jsonify(response), 200

@remessas.route('/estatisticas', methods=['GET'])
@auth_required()
def get_estatisticas():
    """
    Obtém estatísticas das remessas
    ---
    tags:
      - Remessas
    security:
      - BasicAuth: []
    responses:
      200:
        description: Estatísticas das remessas
    """
    # Total de remessas por status
    total_processadas = Remessa.query.filter_by(status='Processado').count()
    total_pendentes = Remessa.query.filter_by(status='Pendente').count()
    total_erros = Remessa.query.filter_by(status='Erro').count()
    
    # Total por tipo
    total_remessas = Remessa.query.filter_by(tipo='Remessa').count()
    total_desistencias = Remessa.query.filter_by(tipo='Desistência').count()
    
    # Total por UF (top 5)
    ufs = db.session.query(
        Remessa.uf, 
        db.func.count(Remessa.id).label('total')
    ).group_by(Remessa.uf).order_by(db.func.count(Remessa.id).desc()).limit(5).all()
    
    # Total de títulos processados
    total_titulos = db.session.query(db.func.sum(Remessa.quantidade_titulos)).scalar() or 0
    
    return jsonify({
        'total_remessas': total_remessas + total_desistencias,
        'por_status': {
            'processadas': total_processadas,
            'pendentes': total_pendentes,
            'erros': total_erros
        },
        'por_tipo': {
            'remessas': total_remessas,
            'desistencias': total_desistencias
        },
        'por_uf': {uf: total for uf, total in ufs},
        'total_titulos': total_titulos
    }), 200

# Rota para exportar remessas para CSV
@remessas.route('/exportar', methods=['GET'])
@auth_required()
def exportar_remessas():
    """
    Exporta remessas para CSV com os mesmos filtros da listagem
    ---
    tags:
      - Remessas
    security:
      - BasicAuth: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de remessa
      - name: uf
        in: query
        type: string
        required: false
        description: UF do cartório
      - name: status
        in: query
        type: string
        required: false
        description: Status da remessa
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
        description: Arquivo CSV com remessas
        content:
          text/csv:
            schema:
              type: string
              format: binary
      400:
        description: Erro nos parâmetros
      500:
        description: Erro ao gerar CSV
    """
    from io import StringIO
    import csv
    from flask import Response
    
    # Obter parâmetros de consulta (mesmos da listagem)
    tipo = request.args.get('tipo')
    uf = request.args.get('uf')
    status = request.args.get('status')
    data_inicio = request.args.get('dataInicio')
    data_fim = request.args.get('dataFim')
    
    # Construir a consulta
    query = Remessa.query
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Remessa.tipo == tipo)
    
    if uf:
        query = query.filter(Remessa.uf == uf)
    
    if status:
        query = query.filter(Remessa.status == status)
    
    if data_inicio:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio >= data_inicio_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataInicio. Use YYYY-MM-DD'}), 400
    
    if data_fim:
        try:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio <= data_fim_dt)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido para dataFim. Use YYYY-MM-DD'}), 400
    
    # Ordenar por data de envio (mais recentes primeiro)
    query = query.order_by(Remessa.data_envio.desc())
    
    # Executar a consulta (sem paginação para exportação)
    try:
        remessas = query.all()
        
        # Criar buffer para CSV
        si = StringIO()
        cw = csv.writer(si)
        
        # Escrever cabeçalho
        cw.writerow(['ID', 'Nome do Arquivo', 'Data de Envio', 'Status', 'UF', 'Tipo', 
                     'Quantidade de Títulos', 'Usuário', 'Data de Processamento', 'Descrição'])
        
        # Escrever dados
        for remessa in remessas:
            usuario = User.query.get(remessa.usuario_id)
            usuario_nome = usuario.nome_completo if usuario else 'N/A'
            
            cw.writerow([
                remessa.id,
                remessa.nome_arquivo,
                remessa.data_envio.strftime('%Y-%m-%d %H:%M:%S') if remessa.data_envio else 'N/A',
                remessa.status,
                remessa.uf,
                remessa.tipo,
                remessa.quantidade_titulos,
                usuario_nome,
                remessa.data_processamento.strftime('%Y-%m-%d %H:%M:%S') if remessa.data_processamento else 'N/A',
                remessa.descricao or 'N/A'
            ])
        
        # Criar resposta com o CSV
        output = si.getvalue()
        
        # Nome do arquivo
        filename = f"remessas_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Retornar CSV como download
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar remessas para CSV: {str(e)}")
        return jsonify({'message': f'Erro ao gerar CSV: {str(e)}'}), 500
