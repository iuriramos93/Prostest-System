import os
import uuid
from datetime import datetime
from flask import request, jsonify, current_app, g
from app.auth.middleware import auth_required
from werkzeug.utils import secure_filename
from app import db
from app.models import Desistencia, Titulo, User, Devedor, Erro
from . import desistencias

# Função auxiliar para verificar se o arquivo é permitido
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'xml', 'pdf', 'doc', 'docx'}

@desistencias.route('/upload', methods=['POST'])
@auth_required()
def upload_desistencia_file():
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
        name: arquivo
        type: file
        required: true
        description: Arquivo de desistência
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
        description: Desistência criada
      400:
        description: Dados inválidos
      404:
        description: Título não encontrado
    """
    try:
        current_app.logger.info("Iniciando processamento de upload de desistência")
        
        current_user = g.user
        user_id = current_user.id if current_user else None
        current_user = User.query.get(user_id)
        
        if not current_user:
            current_app.logger.error(f"Usuário não encontrado: {user_id}")
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se o arquivo foi enviado (verificar tanto 'file' quanto 'arquivo')
        if 'file' not in request.files and 'arquivo' not in request.files:
            current_app.logger.error("Nenhum arquivo enviado no request")
            return jsonify({'message': 'Nenhum arquivo enviado. Verifique se o campo do formulário está nomeado corretamente (deve ser "arquivo").'}), 400
        
        # Obter o arquivo do campo correto
        file = request.files.get('arquivo') or request.files.get('file')
        current_app.logger.info(f"Arquivo recebido: {file.filename if file else 'None'}")
        
        # Verificar se o arquivo tem nome
        if file.filename == '':
            return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar se o arquivo é do tipo permitido
        if not allowed_file(file.filename):
            return jsonify({'message': 'Tipo de arquivo não permitido. Apenas XML, PDF, DOC e DOCX são aceitos'}), 415
        
        # Verificar se UF foi informada
        uf = request.form.get('uf')
        descricao = request.form.get('descricao')
        
        if not uf:
            return jsonify({'message': 'UF é obrigatória'}), 400
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{filename}"
        
        # Criar diretório de upload se não existir
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'desistencias')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        current_app.logger.info(f"Salvando arquivo em: {file_path}")
        
        # Salvar arquivo
        file.save(file_path)
        
        # Criar registro de desistência no banco
        desistencia = Desistencia(
            motivo=descricao or f"Desistência enviada via upload de arquivo - {filename}",
            status='Pendente',
            usuario_id=current_user.id,
            data_solicitacao=datetime.utcnow()
        )
        
        db.session.add(desistencia)
        db.session.commit()
        current_app.logger.info(f"Desistência criada com sucesso: ID {desistencia.id}")
        
        return jsonify({
            'message': 'Solicitação de desistência criada com sucesso',
            'id': str(desistencia.id),
            'dataSolicitacao': desistencia.data_solicitacao.isoformat(),
            'motivo': desistencia.motivo,
            'status': 'Pendente'  # Mantendo consistência com o valor no banco
        }), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao processar upload de desistência: {str(e)}")
        db.session.rollback()
        return jsonify({'message': f'Erro ao processar solicitação: {str(e)}'}), 500
