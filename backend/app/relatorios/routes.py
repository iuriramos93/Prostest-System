from datetime import datetime, timedelta
from io import BytesIO
from flask import request, jsonify, send_file
from app.auth.middleware import auth_required, get_current_user
from sqlalchemy import func, desc, and_, or_
from app import db
from app.models import Titulo, Remessa, Erro, Desistencia, User, Credor, Devedor
from . import relatorios

# Importações para geração de PDF
import pdfkit
import tempfile
import os

@relatorios.route('/titulos', methods=['GET'])
@auth_required()
def relatorio_titulos():
    """
    Gera relatório de títulos com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
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
      - name: formato
        in: query
        type: string
        required: false
        description: Formato do relatório (pdf, json)
        default: json
    responses:
      200:
        description: Relatório de títulos
    """
    # Parâmetros de filtro
    status = request.args.get('status')
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    formato = request.args.get('formato', 'json')
    
    # Construir query base
    query = Titulo.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Titulo.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Titulo.data_emissao >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            query = query.filter(Titulo.data_emissao <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query
    titulos = query.order_by(Titulo.data_cadastro.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    valor_total = 0
    
    for titulo in titulos:
        dados_titulo = {
            'numero': titulo.numero,
            'protocolo': titulo.protocolo,
            'valor': float(titulo.valor) if titulo.valor else 0,
            'data_emissao': titulo.data_emissao.strftime('%d/%m/%Y') if titulo.data_emissao else 'N/A',
            'data_vencimento': titulo.data_vencimento.strftime('%d/%m/%Y') if titulo.data_vencimento else 'N/A',
            'status': titulo.status,
            'devedor': titulo.devedor.nome if titulo.devedor else 'N/A',
            'credor': titulo.credor.nome if titulo.credor else 'N/A'
        }
        dados_relatorio.append(dados_titulo)
        valor_total += float(titulo.valor) if titulo.valor else 0
    
    # Resumo do relatório
    resumo = {
        'total_titulos': len(titulos),
        'valor_total': valor_total,
        'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'filtros_aplicados': {
            'status': status if status else 'Todos',
            'periodo': f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else 'Todo o período'
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == 'pdf':
        return gerar_pdf_titulos(dados_relatorio, resumo)
    else:
        return jsonify({
            'resumo': resumo,
            'titulos': dados_relatorio
        }), 200

@relatorios.route('/remessas', methods=['GET'])
@auth_required()
def relatorio_remessas():
    """
    Gera relatório de remessas com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Status da remessa (Processado, Erro, Pendente)
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
      - name: formato
        in: query
        type: string
        required: false
        description: Formato do relatório (pdf, json)
        default: json
    responses:
      200:
        description: Relatório de remessas
    """
    # Parâmetros de filtro
    status = request.args.get('status')
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    formato = request.args.get('formato', 'json')
    
    # Construir query base
    query = Remessa.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Remessa.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            query = query.filter(Remessa.data_envio <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query
    remessas = query.order_by(Remessa.data_envio.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    total_titulos = 0
    total_erros = 0
    
    for remessa in remessas:
        dados_remessa = {
            'nome_arquivo': remessa.nome_arquivo,
            'data_envio': remessa.data_envio.strftime('%d/%m/%Y %H:%M') if remessa.data_envio else 'N/A',
            'status': remessa.status,
            'tipo': remessa.tipo,
            'quantidade_titulos': remessa.quantidade_titulos,
            'titulos_processados': remessa.titulos.count(),
            'erros': remessa.erros.count(),
            'usuario': remessa.usuario.nome_completo if hasattr(remessa, 'usuario') and remessa.usuario else 'N/A',
            'data_processamento': remessa.data_processamento.strftime('%d/%m/%Y %H:%M') if remessa.data_processamento else 'N/A'
        }
        dados_relatorio.append(dados_remessa)
        total_titulos += remessa.quantidade_titulos
        total_erros += remessa.erros.count()
    
    # Resumo do relatório
    resumo = {
        'total_remessas': len(remessas),
        'total_titulos': total_titulos,
        'total_erros': total_erros,
        'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'filtros_aplicados': {
            'status': status if status else 'Todos',
            'periodo': f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else 'Todo o período'
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == 'pdf':
        return gerar_pdf_remessas(dados_relatorio, resumo)
    else:
        return jsonify({
            'resumo': resumo,
            'remessas': dados_relatorio
        }), 200

@relatorios.route('/erros', methods=['GET'])
@auth_required()
def relatorio_erros():
    """
    Gera relatório de erros com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de erro (Validação, Processamento, Sistema)
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
      - name: formato
        in: query
        type: string
        required: false
        description: Formato do relatório (pdf, json)
        default: json
    responses:
      200:
        description: Relatório de erros
    """
    # Parâmetros de filtro
    tipo = request.args.get('tipo')
    resolvido_str = request.args.get('resolvido')
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    formato = request.args.get('formato', 'json')
    
    # Construir query base
    query = Erro.query
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Erro.tipo == tipo)
    
    if resolvido_str is not None:
        resolvido = resolvido_str.lower() == 'true'
        query = query.filter(Erro.resolvido == resolvido)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            query = query.filter(Erro.data_ocorrencia >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            query = query.filter(Erro.data_ocorrencia <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query
    erros = query.order_by(Erro.data_ocorrencia.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    
    for erro in erros:
        dados_erro = {
            'id': erro.id,
            'tipo': erro.tipo,
            'mensagem': erro.mensagem,
            'data_ocorrencia': erro.data_ocorrencia.strftime('%d/%m/%Y %H:%M') if erro.data_ocorrencia else 'N/A',
            'resolvido': 'Sim' if erro.resolvido else 'Não',
            'data_resolucao': erro.data_resolucao.strftime('%d/%m/%Y %H:%M') if erro.data_resolucao else 'N/A',
            'remessa': erro.remessa.nome_arquivo if erro.remessa else 'N/A',
            'titulo': erro.titulo.numero if erro.titulo else 'N/A',
            'usuario_resolucao': erro.usuario_resolucao.nome_completo if erro.usuario_resolucao else 'N/A'
        }
        dados_relatorio.append(dados_erro)
    
    # Resumo do relatório
    resumo = {
        'total_erros': len(erros),
        'erros_resolvidos': sum(1 for erro in erros if erro.resolvido),
        'erros_pendentes': sum(1 for erro in erros if not erro.resolvido),
        'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'filtros_aplicados': {
            'tipo': tipo if tipo else 'Todos',
            'resolvido': resolvido_str if resolvido_str is not None else 'Todos',
            'periodo': f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else 'Todo o período'
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == 'pdf':
        return gerar_pdf_erros(dados_relatorio, resumo)
    else:
        return jsonify({
            'resumo': resumo,
            'erros': dados_relatorio
        }), 200

@relatorios.route('/desistencias', methods=['GET'])
@auth_required()
def relatorio_desistencias():
    """
    Gera relatório de desistências com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Status da desistência (Aprovada, Pendente, Rejeitada)
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
      - name: formato
        in: query
        type: string
        required: false
        description: Formato do relatório (pdf, json)
        default: json
    responses:
      200:
        description: Relatório de desistências
    """
    # Parâmetros de filtro
    status = request.args.get('status')
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    formato = request.args.get('formato', 'json')
    
    # Construir query base
    query = Desistencia.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Desistencia.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            query = query.filter(Desistencia.data_solicitacao >= data_inicio)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            query = query.filter(Desistencia.data_solicitacao <= data_fim)
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Executar query
    desistencias = query.order_by(Desistencia.data_solicitacao.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    
    for desistencia in desistencias:
        dados_desistencia = {
            'id': desistencia.id,
            'titulo': desistencia.titulo.numero if desistencia.titulo else 'N/A',
            'protocolo': desistencia.titulo.protocolo if desistencia.titulo else 'N/A',
            'devedor': desistencia.titulo.devedor.nome if desistencia.titulo and desistencia.titulo.devedor else 'N/A',
            'motivo': desistencia.motivo,
            'status': desistencia.status,
            'data_solicitacao': desistencia.data_solicitacao.strftime('%d/%m/%Y %H:%M') if desistencia.data_solicitacao else 'N/A',
            'data_processamento': desistencia.data_processamento.strftime('%d/%m/%Y %H:%M') if desistencia.data_processamento else 'N/A',
            'usuario': desistencia.usuario.nome_completo if desistencia.usuario else 'N/A',
            'usuario_processamento': desistencia.usuario_processamento.nome_completo if desistencia.usuario_processamento else 'N/A'
        }
        dados_relatorio.append(dados_desistencia)
    
    # Resumo do relatório
    resumo = {
        'total_desistencias': len(desistencias),
        'aprovadas': sum(1 for d in desistencias if d.status == 'Aprovada'),
        'pendentes': sum(1 for d in desistencias if d.status == 'Pendente'),
        'rejeitadas': sum(1 for d in desistencias if d.status == 'Rejeitada'),
        'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'filtros_aplicados': {
            'status': status if status else 'Todos',
            'periodo': f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else 'Todo o período'
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == 'pdf':
        return gerar_pdf_desistencias(dados_relatorio, resumo)
    else:
        return jsonify({
            'resumo': resumo,
            'desistencias': dados_relatorio
        }), 200

@relatorios.route('/estatisticas', methods=['GET'])
@auth_required()
def estatisticas_processamento():
    """
    Obtém estatísticas de processamento do sistema
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
      - name: periodo
        in: query
        type: string
        required: false
        description: Período para estatísticas (dia, semana, mes, ano)
        default: mes
    responses:
      200:
        description: Estatísticas de processamento
    """
    periodo = request.args.get('periodo', 'mes')
    
    # Definir data de início com base no período
    hoje = datetime.now()
    if periodo == 'dia':
        data_inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semana':
        # Início da semana (segunda-feira)
        dias_para_segunda = hoje.weekday()
        data_inicio = (hoje - timedelta(days=dias_para_segunda)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'ano':
        data_inicio = hoje.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # mes (padrão)
        data_inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Estatísticas de títulos
    titulos_total = Titulo.query.filter(Titulo.data_cadastro >= data_inicio).count()
    titulos_por_status = db.session.query(
        Titulo.status, func.count(Titulo.id)
    ).filter(Titulo.data_cadastro >= data_inicio).group_by(Titulo.status).all()
    
    # Estatísticas de remessas
    remessas_total = Remessa.query.filter(Remessa.data_envio >= data_inicio).count()
    remessas_por_status = db.session.query(
        Remessa.status, func.count(Remessa.id)
    ).filter(Remessa.data_envio >= data_inicio).group_by(Remessa.status).all()
    
    # Estatísticas de erros
    erros_total = Erro.query.filter(Erro.data_ocorrencia >= data_inicio).count()
    erros_resolvidos = Erro.query.filter(Erro.data_ocorrencia >= data_inicio, Erro.resolvido == True).count()
    erros_por_tipo = db.session.query(
        Erro.tipo, func.count(Erro.id)
    ).filter(Erro.data_ocorrencia >= data_inicio).group_by(Erro.tipo).all()
    
    # Estatísticas de desistências
    desistencias_total = Desistencia.query.filter(Desistencia.data_solicitacao >= data_inicio).count()
    desistencias_por_status = db.session.query(
        Desistencia.status, func.count(Desistencia.id)
    ).filter(Desistencia.data_solicitacao >= data_inicio).group_by(Desistencia.status).all()
    
    # Tempo médio de processamento de remessas (em minutos)
    tempo_processamento = db.session.query(
        func.avg(func.extract('epoch', Remessa.data_processamento - Remessa.data_envio) / 60)
    ).filter(
        Remessa.data_envio >= data_inicio,
        Remessa.data_processamento.isnot(None)
    ).scalar()
    
    # Tempo médio de resolução de erros (em horas)
    tempo_resolucao = db.session.query(
        func.avg(func.extract('epoch', Erro.data_resolucao - Erro.data_ocorrencia) / 3600)
    ).filter(
        Erro.data_ocorrencia >= data_inicio,
        Erro.resolvido == True,
        Erro.data_resolucao.isnot(None)
    ).scalar()
    
    return jsonify({
        'periodo': periodo,
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': hoje.strftime('%d/%m/%Y'),
        'titulos': {
            'total': titulos_total,
            'por_status': dict(titulos_por_status)
        },
        'remessas': {
            'total': remessas_total,
            'por_status': dict(remessas_por_status),
            'tempo_medio_processamento_minutos': float(tempo_processamento) if tempo_processamento else 0
        },
        'erros': {
            'total': erros_total,
            'resolvidos': erros_resolvidos,
            'pendentes': erros_total - erros_resolvidos,
            'por_tipo': dict(erros_por_tipo),
            'tempo_medio_resolucao_horas': float(tempo_resolucao) if tempo_resolucao else 0
        },
        'desistencias': {
            'total': desistencias_total,
            'por_status': dict(desistencias_por_status)
        }
    }), 200

@relatorios.route('/metricas', methods=['GET'])
@auth_required()
def metricas_desempenho():
    """
    Obtém métricas de desempenho do sistema
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
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
    responses:
      200:
        description: Métricas de desempenho
    """
    # Parâmetros de filtro
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    # Definir datas padrão se não fornecidas (último mês)
    hoje = datetime.now()
    if not data_fim_str:
        data_fim = hoje
    else:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    if not data_inicio_str:
        data_inicio = hoje - timedelta(days=30)
    else:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    # Métricas de volume
    titulos_por_dia = db.session.query(
        func.date(Titulo.data_cadastro).label('data'),
        func.count(Titulo.id).label('quantidade')
    ).filter(
        Titulo.data_cadastro.between(data_inicio, data_fim)
    ).group_by('data').order_by('data').all()
    
    remessas_por_dia = db.session.query(
        func.date(Remessa.data_envio).label('data'),
        func.count(Remessa.id).label('quantidade')
    ).filter(
        Remessa.data_envio.between(data_inicio, data_fim)
    ).group_by('data').order_by('data').all()
    
    # Métricas de qualidade
    taxa_erro_por_dia = db.session.query(
        func.date(Erro.data_ocorrencia).label('data'),
        func.count(Erro.id).label('erros')
    ).filter(
        Erro.data_ocorrencia.between(data_inicio, data_fim)
    ).group_by('data').order_by('data').all()
    
    # Métricas de tempo
    tempo_processamento_por_dia = db.session.query(
        func.date(Remessa.data_processamento).label('data'),
        func.avg(func.extract('epoch', Remessa.data_processamento - Remessa.data_envio) / 60).label('tempo_minutos')
    ).filter(
        Remessa.data_envio.between(data_inicio, data_fim),
        Remessa.data_processamento.isnot(None)
    ).group_by('data').order_by('data').all()
    
    tempo_resolucao_por_dia = db.session.query(
        func.date(Erro.data_resolucao).label('data'),
        func.avg(func.extract('epoch', Erro.data_resolucao - Erro.data_ocorrencia) / 3600).label('tempo_horas')
    ).filter(
        Erro.data_ocorrencia.between(data_inicio, data_fim),
        Erro.resolvido == True,
        Erro.data_resolucao.isnot(None)
    ).group_by('data').order_by('data').all()
    
    # Formatar resultados
    return jsonify({
        'periodo': {
            'data_inicio': data_inicio.strftime('%d/%m/%Y'),
            'data_fim': data_fim.strftime('%d/%m/%Y')
        },
        'volume': {
            'titulos_por_dia': [
                {'data': data.strftime('%d/%m/%Y'), 'quantidade': quantidade}
                for data, quantidade in titulos_por_dia
            ],
            'remessas_por_dia': [
                {'data': data.strftime('%d/%m/%Y'), 'quantidade': quantidade}
                for data, quantidade in remessas_por_dia
            ]
        },
        'qualidade': {
            'erros_por_dia': [
                {'data': data.strftime('%d/%m/%Y'), 'erros': erros}
                for data, erros in taxa_erro_por_dia
            ]
        },
        'tempo': {
            'processamento_remessas_por_dia': [
                {'data': data.strftime('%d/%m/%Y'), 'tempo_minutos': float(tempo_minutos) if tempo_minutos else 0}
                for data, tempo_minutos in tempo_processamento_por_dia
            ],
            'resolucao_erros_por_dia': [
                {'data': data.strftime('%d/%m/%Y'), 'tempo_horas': float(tempo_horas) if tempo_horas else 0}
                for data, tempo_horas in tempo_resolucao_por_dia
            ]
        }
    }), 200

@relatorios.route('/', methods=['GET'])
@auth_required()
def relatorio_dashboard():
    """
    Retorna dados para o dashboard
    ---
    tags:
      - Relatórios
    security:
      - JWT: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de relatório (dashboard)
    responses:
      200:
        description: Dados do dashboard
    """
    # Obter dados dos últimos 6 meses
    data_inicio = datetime.now() - timedelta(days=180)
    
    # Títulos por status
    titulos_por_status = db.session.query(
        Titulo.status,
        func.count(Titulo.id)
    ).filter(
        Titulo.data_cadastro >= data_inicio
    ).group_by(Titulo.status).all()
    
    # Remessas por mês
    remessas_por_mes = db.session.query(
        func.date_trunc('month', Remessa.data_envio).label('mes'),
        func.count(Remessa.id).label('quantidade')
    ).filter(
        Remessa.data_envio >= data_inicio
    ).group_by('mes').order_by('mes').all()
    
    # Valor total protestado
    valor_total = db.session.query(
        func.sum(Titulo.valor)
    ).filter(
        Titulo.status == 'Protestado',
        Titulo.data_cadastro >= data_inicio
    ).scalar() or 0
    
    # Taxa de sucesso no processamento
    total_remessas = Remessa.query.filter(Remessa.data_envio >= data_inicio).count()
    remessas_sucesso = Remessa.query.filter(
        Remessa.data_envio >= data_inicio,
        Remessa.status == 'Processado'
    ).count()
    
    taxa_sucesso = (remessas_sucesso / total_remessas * 100) if total_remessas > 0 else 0
    
    # Formatar dados para retorno
    return jsonify({
        'titulos_por_status': dict(titulos_por_status),
        'remessas_por_mes': [
            {
                'mes': mes.strftime('%b'),
                'quantidade': quantidade
            }
            for mes, quantidade in remessas_por_mes
        ],
        'valor_total_protestado': float(valor_total),
        'taxa_sucesso_processamento': round(taxa_sucesso, 1)
    }), 200

# Funções auxiliares para geração de PDF
def gerar_pdf_titulos(dados, resumo):
    """
    Gera um PDF com relatório de títulos
    """
    # Criar HTML para o PDF
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Títulos</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; }}
            .resumo {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #3498db; color: white; text-align: left; padding: 8px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Títulos</h1>
        
        <div class="resumo">
            <h2>Resumo</h2>
            <p><strong>Total de Títulos:</strong> {resumo['total_titulos']}</p>
            <p><strong>Valor Total:</strong> R$ {resumo['valor_total']:.2f}</p>
            <p><strong>Data de Geração:</strong> {resumo['data_geracao']}</p>
            <p><strong>Filtros Aplicados:</strong></p>
            <ul>
                <li><strong>Status:</strong> {resumo['filtros_aplicados']['status']}</li>
                <li><strong>Período:</strong> {resumo['filtros_aplicados']['periodo']}</li>
            </ul>
        </div>
        
        <h2>Detalhamento</h2>
        <table>
            <tr>
                <th>Número</th>
                <th>Protocolo</th>
                <th>Valor</th>
                <th>Data Emissão</th>
                <th>Vencimento</th>
                <th>Status</th>
                <th>Devedor</th>
                <th>Credor</th>
            </tr>
    """
    
    # Adicionar linhas da tabela
    for titulo in dados:
        html += f"""
            <tr>
                <td>{titulo['numero']}</td>
                <td>{titulo['protocolo']}</td>
                <td>R$ {titulo['valor']:.2f}</td>
                <td>{titulo['data_emissao']}</td>
                <td>{titulo['data_vencimento']}</td>
                <td>{titulo['status']}</td>
                <td>{titulo['devedor']}</td>
                <td>{titulo['credor']}</td>
            </tr>
        """
    
    # Fechar HTML
    html += f"""
        </table>
        
        <div class="footer">
            <p>Sistema de Protesto - Relatório gerado em {resumo['data_geracao']}</p>
        </div>
    </body>
    </html>
    """
    
    # Gerar PDF a partir do HTML
    try:
        # Criar arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        # Configurar opções do wkhtmltopdf
        options = {
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
        }
        
        # Gerar PDF
        pdfkit.from_string(html, pdf_path, options=options)
        
        # Enviar arquivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"relatorio_titulos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # Em caso de erro, retornar mensagem
        return jsonify({
            'message': f'Erro ao gerar PDF: {str(e)}',
            'resumo': resumo,
            'titulos': dados
        }), 500

def gerar_pdf_remessas(dados, resumo):
    """
    Gera um PDF com relatório de remessas
    """
    # Criar HTML para o PDF
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Remessas</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; }}
            .resumo {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #3498db; color: white; text-align: left; padding: 8px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Remessas</h1>
        
        <div class="resumo">
            <h2>Resumo</h2>
            <p><strong>Total de Remessas:</strong> {resumo['total_remessas']}</p>
            <p><strong>Total de Títulos:</strong> {resumo['total_titulos']}</p>
            <p><strong>Total de Erros:</strong> {resumo['total_erros']}</p>
            <p><strong>Data de Geração:</strong> {resumo['data_geracao']}</p>
            <p><strong>Filtros Aplicados:</strong></p>
            <ul>
                <li><strong>Status:</strong> {resumo['filtros_aplicados']['status']}</li>
                <li><strong>Período:</strong> {resumo['filtros_aplicados']['periodo']}</li>
            </ul>
        </div>
        
        <h2>Detalhamento</h2>
        <table>
            <tr>
                <th>Nome do Arquivo</th>
                <th>Data de Envio</th>
                <th>Status</th>
                <th>Tipo</th>
                <th>Qtd. Títulos</th>
                <th>Títulos Processados</th>
                <th>Erros</th>
                <th>Usuário</th>
                <th>Data Processamento</th>
            </tr>
    """
    
    # Adicionar linhas da tabela
    for remessa in dados:
        html += f"""
            <tr>
                <td>{remessa['nome_arquivo']}</td>
                <td>{remessa['data_envio']}</td>
                <td>{remessa['status']}</td>
                <td>{remessa['tipo']}</td>
                <td>{remessa['quantidade_titulos']}</td>
                <td>{remessa['titulos_processados']}</td>
                <td>{remessa['erros']}</td>
                <td>{remessa['usuario']}</td>
                <td>{remessa['data_processamento']}</td>
            </tr>
        """
    
    # Fechar HTML
    html += f"""
        </table>
        
        <div class="footer">
            <p>Sistema de Protesto - Relatório gerado em {resumo['data_geracao']}</p>
        </div>
    </body>
    </html>
    """
    
    # Gerar PDF a partir do HTML
    try:
        # Criar arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        # Configurar opções do wkhtmltopdf
        options = {
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
        }
        
        # Gerar PDF
        pdfkit.from_string(html, pdf_path, options=options)
        
        # Enviar arquivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"relatorio_remessas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # Em caso de erro, retornar mensagem
        return jsonify({
            'message': f'Erro ao gerar PDF: {str(e)}',
            'resumo': resumo,
            'remessas': dados
        }), 500

def gerar_pdf_erros(dados, resumo):
    """
    Gera um PDF com relatório de erros
    """
    # Criar HTML para o PDF
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Erros</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; }}
            .resumo {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #3498db; color: white; text-align: left; padding: 8px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Erros</h1>
        
        <div class="resumo">
            <h2>Resumo</h2>
            <p><strong>Total de Erros:</strong> {resumo['total_erros']}</p>
            <p><strong>Erros Resolvidos:</strong> {resumo['erros_resolvidos']}</p>
            <p><strong>Erros Pendentes:</strong> {resumo['erros_pendentes']}</p>
            <p><strong>Data de Geração:</strong> {resumo['data_geracao']}</p>
            <p><strong>Filtros Aplicados:</strong></p>
            <ul>
                <li><strong>Tipo:</strong> {resumo['filtros_aplicados']['tipo']}</li>
                <li><strong>Resolvido:</strong> {resumo['filtros_aplicados']['resolvido']}</li>
                <li><strong>Período:</strong> {resumo['filtros_aplicados']['periodo']}</li>
            </ul>
        </div>
        
        <h2>Detalhamento</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Tipo</th>
                <th>Data Ocorrência</th>
                <th>Resolvido</th>
                <th>Data Resolução</th>
                <th>Remessa</th>
                <th>Título</th>
                <th>Usuário Resolução</th>
            </tr>
    """
    
    # Adicionar linhas da tabela
    for erro in dados:
        html += f"""
            <tr>
                <td>{erro['id']}</td>
                <td>{erro['tipo']}</td>
                <td>{erro['data_ocorrencia']}</td>
                <td>{erro['resolvido']}</td>
                <td>{erro['data_resolucao']}</td>
                <td>{erro['remessa']}</td>
                <td>{erro['titulo']}</td>
                <td>{erro['usuario_resolucao']}</td>
            </tr>
        """
    
    # Fechar HTML
    html += f"""
        </table>
        
        <div class="footer">
            <p>Sistema de Protesto - Relatório gerado em {resumo['data_geracao']}</p>
        </div>
    </body>
    </html>
    """
    
    # Gerar PDF a partir do HTML
    try:
        # Criar arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        # Configurar opções do wkhtmltopdf
        options = {
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
        }
        
        # Gerar PDF
        pdfkit.from_string(html, pdf_path, options=options)
        
        # Enviar arquivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"relatorio_erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # Em caso de erro, retornar mensagem
        return jsonify({
            'message': f'Erro ao gerar PDF: {str(e)}',
            'resumo': resumo,
            'erros': dados
        }), 500

def gerar_pdf_desistencias(dados, resumo):
    """
    Gera um PDF com relatório de desistências
    """
    # Criar HTML para o PDF
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Desistências</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; }}
            .resumo {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #3498db; color: white; text-align: left; padding: 8px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Desistências</h1>
        
        <div class="resumo">
            <h2>Resumo</h2>
            <p><strong>Total de Desistências:</strong> {resumo['total_desistencias']}</p>
            <p><strong>Aprovadas:</strong> {resumo['aprovadas']}</p>
            <p><strong>Pendentes:</strong> {resumo['pendentes']}</p>
            <p><strong>Rejeitadas:</strong> {resumo['rejeitadas']}</p>
            <p><strong>Data de Geração:</strong> {resumo['data_geracao']}</p>
            <p><strong>Filtros Aplicados:</strong></p>
            <ul>
                <li><strong>Status:</strong> {resumo['filtros_aplicados']['status']}</li>
                <li><strong>Período:</strong> {resumo['filtros_aplicados']['periodo']}</li>
            </ul>
        </div>
        
        <h2>Detalhamento</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Protocolo</th>
                <th>Devedor</th>
                <th>Motivo</th>
                <th>Status</th>
                <th>Data Solicitação</th>
                <th>Data Processamento</th>
                <th>Usuário</th>
                <th>Usuário Processamento</th>
            </tr>
    """
    
    # Adicionar linhas da tabela
    for desistencia in dados:
        html += f"""
            <tr>
                <td>{desistencia['id']}</td>
                <td>{desistencia['titulo']}</td>
                <td>{desistencia['protocolo']}</td>
                <td>{desistencia['devedor']}</td>
                <td>{desistencia['motivo']}</td>
                <td>{desistencia['status']}</td>
                <td>{desistencia['data_solicitacao']}</td>
                <td>{desistencia['data_processamento']}</td>
                <td>{desistencia['usuario']}</td>
                <td>{desistencia['usuario_processamento']}</td>
            </tr>
        """
    
    # Fechar HTML
    html += f"""
        </table>
        
        <div class="footer">
            <p>Sistema de Protesto - Relatório gerado em {resumo['data_geracao']}</p>
        </div>
    </body>
    </html>
    """
    
    # Gerar PDF a partir do HTML
    try:
        # Criar arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_path = temp_pdf.name
        
        # Configurar opções do wkhtmltopdf
        options = {
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
        }
        
        # Gerar PDF
        pdfkit.from_string(html, pdf_path, options=options)
        
        # Enviar arquivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"relatorio_desistencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # Em caso de erro, retornar mensagem
        return jsonify({
            'message': f'Erro ao gerar PDF: {str(e)}',
            'resumo': resumo,
            'desistencias': dados
        }), 500