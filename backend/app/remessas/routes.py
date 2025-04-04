import os
import uuid
from datetime import datetime
import xmltodict
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
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
@jwt_required()
def upload_remessa():
    """
    Faz upload de um arquivo de remessa
    ---
    tags:
      - Remessas
    security:
      - JWT: []
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
    user_id = get_jwt_identity()
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
            'task_id': task_id
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
            'message': 'Erro ao processar arquivo',
            'error': str(e),
            'remessa': remessa.to_dict()
        }), 500

def processar_remessa(remessa_id, file_path):
    """
    Processa um arquivo de remessa
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
        
        # Processar dados (implementação simplificada)
        # Em um sistema real, isso seria mais complexo e validaria o formato específico do XML
        if remessa.tipo == 'Remessa':
            processar_remessa_titulos(remessa, data)
        else:  # Desistência
            processar_remessa_desistencias(remessa, data)
        
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

def processar_remessa_titulos(remessa, data):
    """
    Processa uma remessa de títulos
    """
    # Implementação simplificada - em um sistema real, isso seria mais complexo
    # e validaria o formato específico do XML de acordo com o layout do CRA/cartório
    
    # Exemplo de estrutura esperada (simplificada):
    # {
    #   "remessa": {
    #     "titulos": {
    #       "titulo": [
    #         { ... dados do título ... },
    #         { ... dados do título ... }
    #       ]
    #     }
    #   }
    # }
    
    titulos_data = []
    
    # Extrair lista de títulos do XML (adaptado para o formato real do XML)
    if 'remessa' in data and 'titulos' in data['remessa']:
        titulos_xml = data['remessa']['titulos']
        
        # Verificar se é uma lista ou um único item
        if 'titulo' in titulos_xml:
            if isinstance(titulos_xml['titulo'], list):
                titulos_data = titulos_xml['titulo']
            else:
                titulos_data = [titulos_xml['titulo']]
    
    # Processar cada título
    for titulo_data in titulos_data:
        try:
            # Processar dados do credor
            credor = None
            if 'credor' in titulo_data:
                credor_data = titulo_data['credor']
                credor = Credor.query.filter_by(documento=credor_data.get('documento')).first()
                
                if not credor:
                    credor = Credor(
                        nome=credor_data.get('nome'),
                        documento=credor_data.get('documento'),
                        endereco=credor_data.get('endereco'),
                        cidade=credor_data.get('cidade'),
                        uf=credor_data.get('uf'),
                        cep=credor_data.get('cep')
                    )
                    db.session.add(credor)
            
            # Processar dados do devedor
            devedor = None
            if 'devedor' in titulo_data:
                devedor_data = titulo_data['devedor']
                devedor = Devedor.query.filter_by(documento=devedor_data.get('documento')).first()
                
                if not devedor:
                    devedor = Devedor(
                        nome=devedor_data.get('nome'),
                        documento=devedor_data.get('documento'),
                        endereco=devedor_data.get('endereco'),
                        cidade=devedor_data.get('cidade'),
                        uf=devedor_data.get('uf'),
                        cep=devedor_data.get('cep')
                    )
                    db.session.add(devedor)
            
            # Commit para obter IDs do credor e devedor
            db.session.flush()
            
            # Criar título
            titulo = Titulo(
                numero=titulo_data.get('numero'),
                protocolo=titulo_data.get('protocolo'),
                valor=float(titulo_data.get('valor', 0)),
                data_emissao=datetime.strptime(titulo_data.get('data_emissao', ''), '%Y-%m-%d').date() if titulo_data.get('data_emissao') else None,
                data_vencimento=datetime.strptime(titulo_data.get('data_vencimento', ''), '%Y-%m-%d').date() if titulo_data.get('data_vencimento') else None,
                status='Pendente',
                remessa_id=remessa.id,
                credor_id=credor.id if credor else None,
                devedor_id=devedor.id if devedor else None,
                especie=titulo_data.get('especie'),
                aceite=titulo_data.get('aceite') == 'S',
                nosso_numero=titulo_data.get('nosso_numero')
            )
            
            db.session.add(titulo)
            remessa.quantidade_titulos += 1
            
        except Exception as e:
            # Registrar erro específico do título
            erro = Erro(
                remessa_id=remessa.id,
                tipo='Validação',
                mensagem=f"Erro ao processar título: {str(e)}\nDados: {titulo_data}",
                data_ocorrencia=datetime.utcnow()
            )
            db.session.add(erro)
    
    # Commit final
    db.session.commit()

def processar_remessa_desistencias(remessa, data):
    """
    Processa uma remessa de desistências
    """
    # Implementação simplificada - em um sistema real, isso seria mais complexo
    # Este é apenas um exemplo básico
    
    # Exemplo de estrutura esperada (simplificada):
    # {
    #   "desistencias": {
    #     "desistencia": [
    #       { "protocolo": "123", "motivo": "Pagamento" },
    #       { "protocolo": "456", "motivo": "Acordo" }
    #     ]
    #   }
    # }
    
    desistencias_data = []
    
    # Extrair lista de desistências do XML (adaptado para o formato real do XML)
    if 'desistencias' in data:
        desistencias_xml = data['desistencias']
        
        # Verificar se é uma lista ou um único item
        if 'desistencia' in desistencias_xml:
            if isinstance(desistencias_xml['desistencia'], list):
                desistencias_data = desistencias_xml['desistencia']
            else:
                desistencias_data = [desistencias_xml['desistencia']]
    
    # Processar cada desistência
    for desistencia_data in desistencias_data:
        try:
            protocolo = desistencia_data.get('protocolo')
            motivo = desistencia_data.get('motivo')
            
            # Buscar título pelo protocolo
            titulo = Titulo.query.filter_by(protocolo=protocolo).first()
            
            if not titulo:
                # Registrar erro
                erro = Erro(
                    remessa_id=remessa.id,
                    tipo='Validação',
                    mensagem=f"Título com protocolo {protocolo} não encontrado",
                    data_ocorrencia=datetime.utcnow()
                )
                db.session.add(erro)
                continue
            
            # Criar desistência
            desistencia = Desistencia(
                titulo_id=titulo.id,
                motivo=motivo,
                status='Pendente',
                usuario_id=remessa.usuario_id
            )
            
            db.session.add(desistencia)
            remessa.quantidade_titulos += 1
            
        except Exception as e:
            # Registrar erro específico da desistência
            erro = Erro(
                remessa_id=remessa.id,
                tipo='Validação',
                mensagem=f"Erro ao processar desistência: {str(e)}\nDados: {desistencia_data}",
                data_ocorrencia=datetime.utcnow()
            )
            db.session.add(erro)
    
    # Commit final
    db.session.commit()

@remessas.route('/', methods=['GET'])
@jwt_required()
def get_remessas():
    """
    Lista remessas com filtros opcionais
    ---
    tags:
      - Remessas
    security:
      - JWT: []
    parameters:
      - name: nome_arquivo
        in: query
        type: string
        required: false
        description: Nome do arquivo
      - name: status
        in: query
        type: string
        required: false
        description: Status da remessa (Processado, Erro, Pendente)
      - name: uf
        in: query
        type: string
        required: false
        description: UF do cartório
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de remessa (Remessa ou Desistência)
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
        description: Lista de remessas
    """
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Construir query base
    query = Remessa.query
    
    # Aplicar filtros
    if request.args.get('nome_arquivo'):
        query = query.filter(Remessa.nome_arquivo.ilike(f'%{request.args.get("nome_arquivo")}%'))
    
    if request.args.get('status'):
        query = query.filter(Remessa.status == request.args.get('status'))
    
    if request.args.get('uf'):
        query = query.filter(Remessa.uf == request.args.get('uf'))
    
    if request.args.get('tipo'):
        query = query.filter(Remessa.tipo == request.args.get('tipo'))
    
    # Filtro por data
    if request.args.get('data_inicio'):
        try:
            data_inicio = datetime.strptime(request.args.get('data_inicio'), '%Y-%m-%d')
            query = query.filter(Remessa.data_envio >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if request.args.get('data_fim'):
        try:
            data_fim = datetime.strptime(request.args.get('data_fim'), '%Y-%m-%d')
            # Adicionar 1 dia para incluir todo o dia final
            query = query.filter(Remessa.data_envio <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query com paginação
    paginated_remessas = query.order_by(Remessa.data_envio.desc()).paginate(page=page, per_page=per_page)
    
    # Formatar resposta
    return jsonify({
        'items': [remessa.to_dict() for remessa in paginated_remessas.items],
        'total': paginated_remessas.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated_remessas.pages
    }), 200

@remessas.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_remessa(id):
    """
    Obtém detalhes de uma remessa específica
    ---
    tags:
      - Remessas
    security:
      - JWT: []
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
    remessa = Remessa.query.get(id)
    
    if not remessa:
        return jsonify({'message': 'Remessa não encontrada'}), 404
    
    # Obter dados relacionados
    remessa_dict = remessa.to_dict()
    
    # Adicionar dados do usuário
    if remessa.usuario_id:
        usuario = User.query.get(remessa.usuario_id)
        if usuario:
            remessa_dict['usuario'] = {
                'id': usuario.id,
                'nome_completo': usuario.nome_completo
            }
    
    # Adicionar títulos
    titulos = Titulo.query.filter_by(remessa_id=remessa.id).all()
    remessa_dict['titulos'] = [titulo.to_dict() for titulo in titulos]
    
    # Adicionar erros
    erros = Erro.query.filter_by(remessa_id=remessa.id).all()
    remessa_dict['erros'] = [erro.to_dict() for erro in erros]
    
    return jsonify(remessa_dict), 200

@remessas.route('/estatisticas', methods=['GET'])
@jwt_required()
def get_estatisticas():
    """
    Obtém estatísticas das remessas
    ---
    tags:
      - Remessas
    security:
      - JWT: []
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