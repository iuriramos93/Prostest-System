import os
import datetime
from flask import request, jsonify, current_app, g
from app.auth.middleware import auth_required
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Titulo, AutorizacaoCancelamento, TransacaoAutorizacaoCancelamento
from . import autorizacoes
from flasgger import swag_from


def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida"""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ["txt"]


@autorizacoes.route("/upload", methods=["POST"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Faz upload de um arquivo de autorização de cancelamento",
    "description": "Recebe um arquivo de autorização de cancelamento no formato IEPTB-SP",
    "parameters": [
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Arquivo de autorização de cancelamento"
        }
    ],
    "responses": {
        200: {
            "description": "Upload realizado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "autorizacao_id": {"type": "integer"}
                }
            }
        },
        400: {
            "description": "Erro no upload do arquivo",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def upload_file():
    """Endpoint para upload de arquivo de autorização de cancelamento"""
    # Verificar se o arquivo foi enviado na requisição
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files["file"]
    
    # Verificar se o arquivo tem nome
    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    # Verificar se o arquivo tem uma extensão permitida
    if not allowed_file(file.filename):
        return jsonify({"error": "Formato de arquivo não permitido. Use .txt"}), 400
    
    # Salvar o arquivo
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    
    # Obter o usuário atual
    current_user = g.user
    current_user_id = current_user.id if current_user else None
    user = User.query.get(current_user_id)
    
    # Criar registro de autorização de cancelamento
    autorizacao = AutorizacaoCancelamento(
        arquivo_nome=filename,
        status="Pendente",
        usuario_id=current_user_id
    )
    
    db.session.add(autorizacao)
    db.session.commit()
    
    # Iniciar processamento do arquivo em background (em uma implementação real, isso seria feito com Celery ou similar)
    # Por enquanto, vamos processar diretamente
    try:
        process_file(file_path, autorizacao.id)
        return jsonify({
            "message": "Arquivo enviado com sucesso e processado",
            "autorizacao_id": autorizacao.id
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500


def process_file(file_path, autorizacao_id):
    """Processa o arquivo de autorização de cancelamento"""
    autorizacao = AutorizacaoCancelamento.query.get(autorizacao_id)
    
    try:
        with open(file_path, "r", encoding="latin-1") as file:
            lines = file.readlines()
        
        # Processar o header do arquivo (registro tipo 0)
        header_line = None
        trailer_line = None
        transaction_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:  # Ignorar linhas vazias
                continue
                
            record_type = line[0:1]
            
            if record_type == "0":  # Header
                header_line = line
            elif record_type == "1":  # Transação
                transaction_lines.append(line)
            elif record_type == "9":  # Trailer
                trailer_line = line
        
        if not header_line:
            raise ValueError("Header do arquivo não encontrado")
            
        if not trailer_line:
            raise ValueError("Trailer do arquivo não encontrado")
        
        # Processar o header
        codigo_apresentante = header_line[1:4].strip()
        nome_apresentante = header_line[4:49].strip()
        data_movimento_str = header_line[49:57].strip()
        quantidade_solicitacoes = int(header_line[57:62].strip() or "0")
        sequencia_registro = header_line[122:127].strip()
        
        # Converter data do movimento
        data_movimento = datetime.datetime.strptime(data_movimento_str, "%d%m%Y").date() if data_movimento_str else None
        
        # Atualizar o registro de autorização
        autorizacao.codigo_apresentante = codigo_apresentante
        autorizacao.nome_apresentante = nome_apresentante
        autorizacao.data_movimento = data_movimento
        autorizacao.quantidade_solicitacoes = quantidade_solicitacoes
        autorizacao.sequencia_registro = sequencia_registro
        
        # Processar as transações
        for line in transaction_lines:
            numero_protocolo = line[1:11].strip()
            data_protocolizacao_str = line[11:19].strip()
            numero_titulo = line[19:30].strip()
            nome_devedor = line[30:75].strip()
            valor_titulo_str = line[75:89].strip()
            solicitacao_cancelamento = line[89:90].strip()
            agencia_conta = line[90:102].strip()
            carteira_nosso_numero = line[102:114].strip()
            numero_controle = line[116:122].strip()
            sequencia_registro_transacao = line[122:127].strip()
            
            # Converter data de protocolização
            data_protocolizacao = datetime.datetime.strptime(data_protocolizacao_str, "%d%m%Y").date() if data_protocolizacao_str else None
            
            # Converter valor do título (formato: 12 dígitos inteiros + 2 decimais sem separador)
            valor_titulo = float(valor_titulo_str) / 100 if valor_titulo_str else 0
            
            # Buscar título pelo protocolo
            titulo = Titulo.query.filter_by(protocolo=numero_protocolo).first()
            titulo_id = titulo.id if titulo else None
            
            # Criar transação
            transacao = TransacaoAutorizacaoCancelamento(
                autorizacao_id=autorizacao.id,
                titulo_id=titulo_id,
                numero_protocolo=numero_protocolo,
                data_protocolizacao=data_protocolizacao,
                numero_titulo=numero_titulo,
                nome_devedor=nome_devedor,
                valor_titulo=valor_titulo,
                solicitacao_cancelamento=solicitacao_cancelamento,
                agencia_conta=agencia_conta,
                carteira_nosso_numero=carteira_nosso_numero,
                numero_controle=numero_controle,
                sequencia_registro=sequencia_registro_transacao,
                status="Pendente"
            )
            
            db.session.add(transacao)
        
        # Verificar se a quantidade de transações corresponde ao informado no header
        if len(transaction_lines) != quantidade_solicitacoes:
            autorizacao.status = "Erro"
        else:
            autorizacao.status = "Processado"
            
        autorizacao.data_processamento = datetime.datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        autorizacao.status = "Erro"
        db.session.commit()
        raise e


@autorizacoes.route("/", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Lista todas as autorizações de cancelamento",
    "description": "Retorna uma lista de todas as autorizações de cancelamento",
    "responses": {
        200: {
            "description": "Lista de autorizações de cancelamento",
            "schema": {
                "type": "object",
                "properties": {
                    "autorizacoes": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    }
})
def get_autorizacoes():
    """Endpoint para listar todas as autorizações de cancelamento"""
    autorizacoes = AutorizacaoCancelamento.query.all()
    return jsonify({
        "autorizacoes": [a.to_dict() for a in autorizacoes]
    })


@autorizacoes.route("/<int:id>", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Obtém detalhes de uma autorização de cancelamento",
    "description": "Retorna os detalhes de uma autorização de cancelamento específica",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da autorização de cancelamento"
        }
    ],
    "responses": {
        200: {
            "description": "Detalhes da autorização de cancelamento",
            "schema": {
                "type": "object"
            }
        },
        404: {
            "description": "Autorização de cancelamento não encontrada",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def get_autorizacao(id):
    """Endpoint para obter detalhes de uma autorização de cancelamento"""
    autorizacao = AutorizacaoCancelamento.query.get(id)
    
    if not autorizacao:
        return jsonify({"error": "Autorização de cancelamento não encontrada"}), 404
    
    return jsonify(autorizacao.to_dict())


@autorizacoes.route("/<int:id>/transacoes", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Lista as transações de uma autorização de cancelamento",
    "description": "Retorna uma lista de todas as transações de uma autorização de cancelamento específica",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da autorização de cancelamento"
        }
    ],
    "responses": {
        200: {
            "description": "Lista de transações",
            "schema": {
                "type": "object",
                "properties": {
                    "transacoes": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Autorização de cancelamento não encontrada",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def get_transacoes(id):
    """Endpoint para listar as transações de uma autorização de cancelamento"""
    autorizacao = AutorizacaoCancelamento.query.get(id)
    
    if not autorizacao:
        return jsonify({"error": "Autorização de cancelamento não encontrada"}), 404
    
    transacoes = TransacaoAutorizacaoCancelamento.query.filter_by(autorizacao_id=id).all()
    return jsonify({
        "transacoes": [t.to_dict() for t in transacoes]
    })


@autorizacoes.route("/transacoes/<int:id>/processar", methods=["POST"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Processa uma transação de autorização de cancelamento",
    "description": "Processa uma transação específica de autorização de cancelamento",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da transação"
        }
    ],
    "responses": {
        200: {
            "description": "Transação processada com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "transacao": {"type": "object"}
                }
            }
        },
        404: {
            "description": "Transação não encontrada",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def processar_transacao(id):
    """Endpoint para processar uma transação de autorização de cancelamento"""
    transacao = TransacaoAutorizacaoCancelamento.query.get(id)
    
    if not transacao:
        return jsonify({"error": "Transação não encontrada"}), 404
    
    # Verificar se o título existe
    if not transacao.titulo_id:
        titulo = Titulo.query.filter_by(protocolo=transacao.numero_protocolo).first()
        if titulo:
            transacao.titulo_id = titulo.id
        else:
            return jsonify({"error": "Título não encontrado com o protocolo informado"}), 404
    
    titulo = Titulo.query.get(transacao.titulo_id)
    
    # Verificar se o título está protestado
    if titulo.status != "Protestado":
        return jsonify({"error": "Título não está protestado, não é possível cancelar"}), 400
    
    # Atualizar status do título
    titulo.status = "Cancelado"
    
    # Atualizar status da transação
    transacao.status = "Processado"
    transacao.data_processamento = datetime.datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        "message": "Transação processada com sucesso",
        "transacao": transacao.to_dict()
    })


@autorizacoes.route("/gerar-arquivo-exemplo", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["Autorizações de Cancelamento"],
    "summary": "Gera um arquivo de exemplo de autorização de cancelamento",
    "description": "Gera um arquivo de exemplo no formato IEPTB-SP para autorização de cancelamento",
    "responses": {
        200: {
            "description": "Arquivo gerado com sucesso",
            "content": {
                "application/octet-stream": {}
            }
        }
    }
})
def gerar_arquivo_exemplo():
    """Endpoint para gerar um arquivo de exemplo de autorização de cancelamento"""
    # Dados de exemplo
    codigo_apresentante = "001"
    nome_apresentante = "BANCO EXEMPLO S.A."
    data_movimento = datetime.datetime.now().strftime("%d%m%Y")
    quantidade_solicitacoes = 2
    
    # Criar conteúdo do arquivo
    content = []
    
    # Header
    header = f"0{codigo_apresentante}{nome_apresentante.ljust(45)}{data_movimento}{str(quantidade_solicitacoes).zfill(5)}{' ' * 60}00001"
    content.append(header)
    
    # Transações
    transacao1 = f"1PROT12345{data_movimento}12345678901DEVEDOR EXEMPLO 1{{'0' * 14}}A{{' ' * 12}}67890{{' ' * 8}}00002"
    content.append(transacao1)
    transacao2 = f"1PROT67890{data_movimento}98765432109DEVEDOR EXEMPLO 2{{'0' * 14}}A{{' ' * 12}}12345{{' ' * 8}}00003"
    content.append(transacao2)
    
    # Trailer
    trailer = f"9{codigo_apresentante}{nome_apresentante.ljust(45)}{data_movimento}{str(quantidade_solicitacoes).zfill(5)}{' ' * 60}00004"
    content.append(trailer)
    
    # Criar arquivo temporário
    filename = f"AC{codigo_apresentante}_{data_movimento}.txt"
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    with open(file_path, "w", encoding="latin-1") as f:
        f.write("\n".join(content))
    
    # Retornar o arquivo para download
    return current_app.send_file(file_path, as_attachment=True, download_name=filename)


