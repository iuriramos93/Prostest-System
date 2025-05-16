from datetime import datetime, timedelta
from io import BytesIO
from flask import request, jsonify, send_file, g
from app.auth.middleware import auth_required
from sqlalchemy import func, desc, and_, or_, case
from app import db
from app.models import Titulo, Remessa, Erro, Desistencia, User, Credor, Devedor
from . import relatorios
from app.utils.performance import cache_result, log_performance
from app.utils.export import export_to_csv, export_to_excel, export_to_pdf

# Importações para geração de PDF
import pdfkit
import tempfile
import os
import json

@relatorios.route("/titulos", methods=["GET"])
@auth_required()
def relatorio_titulos():
    """
    Gera relatório de títulos com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
    status = request.args.get("status")
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    formato = request.args.get("formato", "json")
    
    # Construir query base
    query = Titulo.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Titulo.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Executar query
    titulos = query.order_by(Titulo.data_cadastro.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    valor_total = 0
    
    for titulo in titulos:
        dados_titulo = {
            "numero": titulo.numero,
            "protocolo": titulo.protocolo,
            "valor": float(titulo.valor) if titulo.valor else 0,
            "data_emissao": titulo.data_emissao.strftime("%d/%m/%Y") if titulo.data_emissao else "N/A",
            "data_vencimento": titulo.data_vencimento.strftime("%d/%m/%Y") if titulo.data_vencimento else "N/A",
            "status": titulo.status,
            "devedor": titulo.devedor.nome if titulo.devedor else "N/A",
            "credor": titulo.credor.nome if titulo.credor else "N/A"
        }
        dados_relatorio.append(dados_titulo)
        valor_total += float(titulo.valor) if titulo.valor else 0
    
    # Resumo do relatório
    resumo = {
        "total_titulos": len(titulos),
        "valor_total": valor_total,
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "filtros_aplicados": {
            "status": status if status else "Todos",
            "periodo": f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else "Todo o período"
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == "pdf":
        return gerar_pdf_titulos(dados_relatorio, resumo)
    else:
        return jsonify({
            "resumo": resumo,
            "titulos": dados_relatorio
        }), 200

@relatorios.route("/remessas", methods=["GET"])
@auth_required()
def relatorio_remessas():
    """
    Gera relatório de remessas com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
    status = request.args.get("status")
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    formato = request.args.get("formato", "json")
    
    # Construir query base
    query = Remessa.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Remessa.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Remessa.data_envio >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Remessa.data_envio <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Executar query
    remessas = query.order_by(Remessa.data_envio.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    total_titulos = 0
    total_erros = 0
    
    for remessa in remessas:
        dados_remessa = {
            "nome_arquivo": remessa.nome_arquivo,
            "data_envio": remessa.data_envio.strftime("%d/%m/%Y %H:%M") if remessa.data_envio else "N/A",
            "status": remessa.status,
            "tipo": remessa.tipo,
            "quantidade_titulos": remessa.quantidade_titulos,
            "titulos_processados": remessa.titulos.count(),
            "erros": remessa.erros.count(),
            "usuario": remessa.usuario.nome_completo if hasattr(remessa, "usuario") and remessa.usuario else "N/A",
            "data_processamento": remessa.data_processamento.strftime("%d/%m/%Y %H:%M") if remessa.data_processamento else "N/A"
        }
        dados_relatorio.append(dados_remessa)
        total_titulos += remessa.quantidade_titulos
        total_erros += remessa.erros.count()
    
    # Resumo do relatório
    resumo = {
        "total_remessas": len(remessas),
        "total_titulos": total_titulos,
        "total_erros": total_erros,
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "filtros_aplicados": {
            "status": status if status else "Todos",
            "periodo": f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else "Todo o período"
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == "pdf":
        return gerar_pdf_remessas(dados_relatorio, resumo)
    else:
        return jsonify({
            "resumo": resumo,
            "remessas": dados_relatorio
        }), 200

@relatorios.route("/erros", methods=["GET"])
@auth_required()
def relatorio_erros():
    """
    Gera relatório de erros com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
    tipo = request.args.get("tipo")
    resolvido_str = request.args.get("resolvido")
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    formato = request.args.get("formato", "json")
    
    # Construir query base
    query = Erro.query
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Erro.tipo == tipo)
    
    if resolvido_str is not None:
        resolvido = resolvido_str.lower() == "true"
        query = query.filter(Erro.resolvido == resolvido)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Erro.data_ocorrencia >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Erro.data_ocorrencia <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Executar query
    erros = query.order_by(Erro.data_ocorrencia.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    
    for erro in erros:
        dados_erro = {
            "id": erro.id,
            "tipo": erro.tipo,
            "mensagem": erro.mensagem,
            "data_ocorrencia": erro.data_ocorrencia.strftime("%d/%m/%Y %H:%M") if erro.data_ocorrencia else "N/A",
            "resolvido": "Sim" if erro.resolvido else "Não",
            "data_resolucao": erro.data_resolucao.strftime("%d/%m/%Y %H:%M") if erro.data_resolucao else "N/A",
            "remessa": erro.remessa.nome_arquivo if erro.remessa else "N/A",
            "titulo": erro.titulo.numero if erro.titulo else "N/A",
            "usuario_resolucao": erro.usuario_resolucao.nome_completo if erro.usuario_resolucao else "N/A"
        }
        dados_relatorio.append(dados_erro)
    
    # Resumo do relatório
    resumo = {
        "total_erros": len(erros),
        "erros_resolvidos": sum(1 for erro in erros if erro.resolvido),
        "erros_pendentes": sum(1 for erro in erros if not erro.resolvido),
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "filtros_aplicados": {
            "tipo": tipo if tipo else "Todos",
            "resolvido": resolvido_str if resolvido_str is not None else "Todos",
            "periodo": f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else "Todo o período"
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == "pdf":
        return gerar_pdf_erros(dados_relatorio, resumo)
    else:
        return jsonify({
            "resumo": resumo,
            "erros": dados_relatorio
        }), 200

@relatorios.route("/desistencias", methods=["GET"])
@auth_required()
def relatorio_desistencias():
    """
    Gera relatório de desistências com filtros opcionais
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
    status = request.args.get("status")
    data_inicio_str = request.args.get("data_inicio")
    data_fim_str = request.args.get("data_fim")
    formato = request.args.get("formato", "json")
    
    # Construir query base
    query = Desistencia.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Desistencia.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Desistencia.data_solicitacao >= data_inicio)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Desistencia.data_solicitacao <= data_fim)
        except ValueError:
            return jsonify({"message": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Executar query
    desistencias = query.order_by(Desistencia.data_solicitacao.desc()).all()
    
    # Preparar dados para o relatório
    dados_relatorio = []
    
    for desistencia in desistencias:
        dados_desistencia = {
            "id": desistencia.id,
            "titulo": desistencia.titulo.numero if desistencia.titulo else "N/A",
            "protocolo": desistencia.titulo.protocolo if desistencia.titulo else "N/A",
            "devedor": desistencia.titulo.devedor.nome if desistencia.titulo and desistencia.titulo.devedor else "N/A",
            "motivo": desistencia.motivo,
            "status": desistencia.status,
            "data_solicitacao": desistencia.data_solicitacao.strftime("%d/%m/%Y %H:%M") if desistencia.data_solicitacao else "N/A",
            "data_processamento": desistencia.data_processamento.strftime("%d/%m/%Y %H:%M") if desistencia.data_processamento else "N/A",
            "usuario": desistencia.usuario.nome_completo if desistencia.usuario else "N/A",
            "usuario_processamento": desistencia.usuario_processamento.nome_completo if desistencia.usuario_processamento else "N/A"
        }
        dados_relatorio.append(dados_desistencia)
    
    # Resumo do relatório
    resumo = {
        "total_desistencias": len(desistencias),
        "aprovadas": sum(1 for d in desistencias if d.status == "Aprovada"),
        "pendentes": sum(1 for d in desistencias if d.status == "Pendente"),
        "rejeitadas": sum(1 for d in desistencias if d.status == "Rejeitada"),
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "filtros_aplicados": {
            "status": status if status else "Todos",
            "periodo": f"{data_inicio_str} a {data_fim_str}" if data_inicio_str and data_fim_str else "Todo o período"
        }
    }
    
    # Retornar no formato solicitado
    if formato.lower() == "pdf":
        return gerar_pdf_desistencias(dados_relatorio, resumo)
    else:
        return jsonify({
            "resumo": resumo,
            "desistencias": dados_relatorio
        }), 200

@relatorios.route("/estatisticas", methods=["GET"])
@auth_required()
@cache_result(timeout=300)  # Cache por 5 minutos
@log_performance
def estatisticas_processamento():
    """
    Obtém estatísticas de processamento do sistema
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
    # Parâmetro de período
    periodo = request.args.get("periodo", "mes")
    
    # Definir datas de início e fim com base no período
    hoje = datetime.utcnow().date()
    data_fim = datetime.combine(hoje + timedelta(days=1), datetime.min.time())  # Fim do dia de hoje
    
    if periodo == "dia":
        data_inicio = datetime.combine(hoje, datetime.min.time())  # Início do dia de hoje
    elif periodo == "semana":
        data_inicio = datetime.combine(hoje - timedelta(days=7), datetime.min.time())
    elif periodo == "ano":
        data_inicio = datetime.combine(hoje.replace(month=1, day=1), datetime.min.time())
    else:  # mes (padrão)
        data_inicio = datetime.combine(hoje.replace(day=1), datetime.min.time())
    
    # Estatísticas de Títulos
    total_titulos_periodo = Titulo.query.filter(
        Titulo.data_cadastro >= data_inicio,
        Titulo.data_cadastro < data_fim
    ).count()
    titulos_protestados_periodo = Titulo.query.filter(
        Titulo.status == "Protestado",
        Titulo.data_protesto >= data_inicio,
        Titulo.data_protesto < data_fim
    ).count()
    
    # Estatísticas de Remessas
    remessas_enviadas_periodo = Remessa.query.filter(
        Remessa.data_envio >= data_inicio,
        Remessa.data_envio < data_fim
    ).count()
    remessas_processadas_periodo = Remessa.query.filter(
        Remessa.status == "Processado",
        Remessa.data_processamento >= data_inicio,
        Remessa.data_processamento < data_fim
    ).count()
    remessas_com_erro_periodo = Remessa.query.filter(
        Remessa.status == "Erro",
        Remessa.data_processamento >= data_inicio, # ou data_envio se preferir
        Remessa.data_processamento < data_fim
    ).count()
    
    # Estatísticas de Erros
    erros_ocorridos_periodo = Erro.query.filter(
        Erro.data_ocorrencia >= data_inicio,
        Erro.data_ocorrencia < data_fim
    ).count()
    erros_resolvidos_periodo = Erro.query.filter(
        Erro.resolvido == True,
        Erro.data_resolucao >= data_inicio,
        Erro.data_resolucao < data_fim
    ).count()
    
    # Estatísticas de Desistências
    desistencias_solicitadas_periodo = Desistencia.query.filter(
        Desistencia.data_solicitacao >= data_inicio,
        Desistencia.data_solicitacao < data_fim
    ).count()
    desistencias_aprovadas_periodo = Desistencia.query.filter(
        Desistencia.status == "Aprovada",
        Desistencia.data_processamento >= data_inicio,
        Desistencia.data_processamento < data_fim
    ).count()
    
    return jsonify({
        "periodo_analisado": {
            "de": data_inicio.strftime("%d/%m/%Y"),
            "ate": (data_fim - timedelta(days=1)).strftime("%d/%m/%Y") # Ajustar para mostrar o último dia do período
        },
        "titulos": {
            "total_registrados_periodo": total_titulos_periodo,
            "protestados_periodo": titulos_protestados_periodo
        },
        "remessas": {
            "enviadas_periodo": remessas_enviadas_periodo,
            "processadas_periodo": remessas_processadas_periodo,
            "com_erro_periodo": remessas_com_erro_periodo
        },
        "erros": {
            "ocorridos_periodo": erros_ocorridos_periodo,
            "resolvidos_periodo": erros_resolvidos_periodo
        },
        "desistencias": {
            "solicitadas_periodo": desistencias_solicitadas_periodo,
            "aprovadas_periodo": desistencias_aprovadas_periodo
        }
    }), 200

# Novo endpoint para o dashboard
@relatorios.route("", methods=["GET"])
@auth_required()
def listar_relatorios():
    """
    Lista relatórios disponíveis ou retorna dados para o dashboard
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
    parameters:
      - name: tipo
        in: query
        type: string
        required: false
        description: Tipo de relatório (dashboard para dados do dashboard)
    responses:
      200:
        description: Lista de relatórios ou dados do dashboard
    """
    tipo = request.args.get("tipo")
    
    # Se o tipo for dashboard, retornar dados para o dashboard
    if tipo == "dashboard":
        return obter_dados_dashboard()
    
    # Caso contrário, listar relatórios disponíveis
    relatorios_disponiveis = [
        {
            "id": 1,
            "nome": "Relatório de Títulos",
            "descricao": "Relatório detalhado de títulos com filtros por status e período",
            "tipo": "titulos",
            "parametros": {
                "status": "opcional",
                "data_inicio": "opcional",
                "data_fim": "opcional",
                "formato": "opcional (json/pdf)"
            },
            "data_criacao": datetime.now().isoformat(),
            "usuario_id": g.user.id if g.user else None
        },
        {
            "id": 2,
            "nome": "Relatório de Remessas",
            "descricao": "Relatório de remessas enviadas com status de processamento",
            "tipo": "remessas",
            "parametros": {
                "status": "opcional",
                "data_inicio": "opcional",
                "data_fim": "opcional",
                "formato": "opcional (json/pdf)"
            },
            "data_criacao": datetime.now().isoformat(),
            "usuario_id": g.user.id if g.user else None
        },
        {
            "id": 3,
            "nome": "Relatório de Erros",
            "descricao": "Relatório de erros ocorridos no sistema",
            "tipo": "erros",
            "parametros": {
                "tipo": "opcional",
                "resolvido": "opcional",
                "data_inicio": "opcional",
                "data_fim": "opcional",
                "formato": "opcional (json/pdf)"
            },
            "data_criacao": datetime.now().isoformat(),
            "usuario_id": g.user.id if g.user else None
        },
        {
            "id": 4,
            "nome": "Relatório de Desistências",
            "descricao": "Relatório de desistências de protesto",
            "tipo": "desistencias",
            "parametros": {
                "status": "opcional",
                "data_inicio": "opcional",
                "data_fim": "opcional",
                "formato": "opcional (json/pdf)"
            },
            "data_criacao": datetime.now().isoformat(),
            "usuario_id": g.user.id if g.user else None
        },
        {
            "id": 5,
            "nome": "Estatísticas de Processamento",
            "descricao": "Estatísticas gerais de processamento do sistema",
            "tipo": "estatisticas",
            "parametros": {
                "periodo": "opcional (dia/semana/mes/ano)"
            },
            "data_criacao": datetime.now().isoformat(),
            "usuario_id": g.user.id if g.user else None
        }
    ]
    
    return jsonify(relatorios_disponiveis), 200

def obter_dados_dashboard():
    """
    Função auxiliar para obter dados do dashboard
    """
    try:
        # Obter distribuição de títulos por status
        titulos_por_status = db.session.query(
            Titulo.status, func.count(Titulo.id)
        ).group_by(Titulo.status).all()
        
        # Converter para dicionário
        status_counts = {status: count for status, count in titulos_por_status}
        
        # Obter remessas por mês (últimos 6 meses)
        hoje = datetime.utcnow().date()
        data_inicio = hoje.replace(day=1) - timedelta(days=180)  # 6 meses atrás
        
        remessas_por_mes = db.session.query(
            func.date_trunc('month', Remessa.data_envio).label('mes'),
            func.count().label('quantidade')
        ).filter(
            Remessa.data_envio >= data_inicio
        ).group_by('mes').order_by('mes').all()
        
        # Formatar dados de remessas por mês
        remessas_mes_formatado = [
            {
                "mes": mes.strftime("%Y-%m"),
                "quantidade": quantidade
            } for mes, quantidade in remessas_por_mes
        ]
        
        # Calcular valor total protestado
        valor_total_protestado = db.session.query(
            func.sum(Titulo.valor)
        ).filter(
            Titulo.status == "Protestado"
        ).scalar() or 0
        
        # Calcular taxa de sucesso de processamento
        total_remessas = Remessa.query.count()
        remessas_processadas = Remessa.query.filter(Remessa.status == "Processado").count()
        
        taxa_sucesso = (remessas_processadas / total_remessas * 100) if total_remessas > 0 else 0
        
        # Montar resposta
        return jsonify({
            "titulos_por_status": status_counts,
            "remessas_por_mes": remessas_mes_formatado,
            "valor_total_protestado": float(valor_total_protestado),
            "taxa_sucesso_processamento": float(taxa_sucesso)
        }), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
        return jsonify({"error": f"Erro ao processar solicitação: {str(e)}"}), 500

# Funções auxiliares para gerar PDF (exemplo básico)
def gerar_pdf_titulos(dados, resumo):
    html = "<h1>Relatório de Títulos</h1>"
    html += f"<p>Total de Títulos: {resumo['total_titulos']}</p>"
    html += f"<p>Valor Total: R$ {resumo['valor_total']:.2f}</p>"
    html += f"<p>Gerado em: {resumo['data_geracao']}</p>"
    html += "<table border=\"1\" style=\"width:100%; border-collapse: collapse;\">"
    html += "<tr><th>Número</th><th>Protocolo</th><th>Valor</th><th>Emissão</th><th>Vencimento</th><th>Status</th><th>Devedor</th><th>Credor</th></tr>"
    for titulo in dados:
        html += f"<tr><td>{titulo['numero']}</td><td>{titulo['protocolo']}</td><td>R$ {titulo['valor']:.2f}</td><td>{titulo['data_emissao']}</td><td>{titulo['data_vencimento']}</td><td>{titulo['status']}</td><td>{titulo['devedor']}</td><td>{titulo['credor']}</td></tr>"
    html += "</table>"
    
    try:
        # Salvar HTML em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html_file:
            tmp_html_file.write(html.encode("utf-8"))
            html_path = tmp_html_file.name

        # Converter HTML para PDF usando pdfkit
        pdf_path = html_path.replace(".html", ".pdf")
        pdfkit.from_file(html_path, pdf_path)
        
        # Ler o PDF gerado e enviar como resposta
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        # Remover arquivos temporários
        os.remove(html_path)
        os.remove(pdf_path)
            
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="relatorio_titulos.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500

def gerar_pdf_remessas(dados, resumo):
    html = "<h1>Relatório de Remessas</h1>"
    html += f"<p>Total de Remessas: {resumo['total_remessas']}</p>"
    html += f"<p>Total de Títulos: {resumo['total_titulos']}</p>"
    html += f"<p>Total de Erros: {resumo['total_erros']}</p>"
    html += f"<p>Gerado em: {resumo['data_geracao']}</p>"
    html += "<table border=\"1\" style=\"width:100%; border-collapse: collapse;\">"
    html += "<tr><th>Arquivo</th><th>Data Envio</th><th>Status</th><th>Tipo</th><th>Qtd. Títulos</th><th>Títulos Processados</th><th>Erros</th><th>Usuário</th><th>Data Processamento</th></tr>"
    for remessa in dados:
        html += f"<tr><td>{remessa['nome_arquivo']}</td><td>{remessa['data_envio']}</td><td>{remessa['status']}</td><td>{remessa['tipo']}</td><td>{remessa['quantidade_titulos']}</td><td>{remessa['titulos_processados']}</td><td>{remessa['erros']}</td><td>{remessa['usuario']}</td><td>{remessa['data_processamento']}</td></tr>"
    html += "</table>"
    
    try:
        # Salvar HTML em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html_file:
            tmp_html_file.write(html.encode("utf-8"))
            html_path = tmp_html_file.name

        # Converter HTML para PDF usando pdfkit
        pdf_path = html_path.replace(".html", ".pdf")
        pdfkit.from_file(html_path, pdf_path)
        
        # Ler o PDF gerado e enviar como resposta
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        # Remover arquivos temporários
        os.remove(html_path)
        os.remove(pdf_path)
            
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="relatorio_remessas.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500

def gerar_pdf_erros(dados, resumo):
    html = "<h1>Relatório de Erros</h1>"
    html += f"<p>Total de Erros: {resumo['total_erros']}</p>"
    html += f"<p>Erros Resolvidos: {resumo['erros_resolvidos']}</p>"
    html += f"<p>Erros Pendentes: {resumo['erros_pendentes']}</p>"
    html += f"<p>Gerado em: {resumo['data_geracao']}</p>"
    html += "<table border=\"1\" style=\"width:100%; border-collapse: collapse;\">"
    html += "<tr><th>ID</th><th>Tipo</th><th>Mensagem</th><th>Data Ocorrência</th><th>Resolvido</th><th>Data Resolução</th><th>Remessa</th><th>Título</th><th>Usuário Resolução</th></tr>"
    for erro in dados:
        html += f"<tr><td>{erro['id']}</td><td>{erro['tipo']}</td><td>{erro['mensagem']}</td><td>{erro['data_ocorrencia']}</td><td>{erro['resolvido']}</td><td>{erro['data_resolucao']}</td><td>{erro['remessa']}</td><td>{erro['titulo']}</td><td>{erro['usuario_resolucao']}</td></tr>"
    html += "</table>"
    
    try:
        # Salvar HTML em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html_file:
            tmp_html_file.write(html.encode("utf-8"))
            html_path = tmp_html_file.name

        # Converter HTML para PDF usando pdfkit
        pdf_path = html_path.replace(".html", ".pdf")
        pdfkit.from_file(html_path, pdf_path)
        
        # Ler o PDF gerado e enviar como resposta
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        # Remover arquivos temporários
        os.remove(html_path)
        os.remove(pdf_path)
            
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="relatorio_erros.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500

def gerar_pdf_desistencias(dados, resumo):
    """
    Função auxiliar para gerar PDF de desistências
    """
    try:
        # Criar tabela HTML para dados
        html_table = "<table border='1' cellspacing='0' cellpadding='5'>"
        html_table += "<tr><th>ID</th><th>Data</th><th>Título</th><th>Devedor</th><th>Motivo</th><th>Status</th></tr>"
        
        for desistencia in dados:
            html_table += f"<tr>"
            html_table += f"<td>{desistencia['id']}</td>"
            html_table += f"<td>{desistencia['data_solicitacao']}</td>"
            html_table += f"<td>{desistencia['titulo']}</td>"
            html_table += f"<td>{desistencia['devedor']}</td>"
            html_table += f"<td>{desistencia['motivo']}</td>"
            html_table += f"<td>{desistencia['status']}</td>"
            html_table += f"</tr>"
        
        html_table += "</table>"
        
        # Criar HTML completo
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th {{ background-color: #f2f2f2; }}
                td, th {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                .resumo {{ margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Desistências</h1>
            <div class="resumo">
                <p><strong>Total de desistências:</strong> {resumo['total_desistencias']}</p>
                <p><strong>Aprovadas:</strong> {resumo['aprovadas']}</p>
                <p><strong>Pendentes:</strong> {resumo['pendentes']}</p>
                <p><strong>Rejeitadas:</strong> {resumo['rejeitadas']}</p>
                <p><strong>Data de geração:</strong> {resumo['data_geracao']}</p>
            </div>
            {html_table}
        </body>
        </html>
        """
        
        # Gerar PDF
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdfkit.from_string(html_content, pdf_file.name)
        pdf_file.close()
        
        # Enviar PDF como download
        return send_file(
            pdf_file.name,
            as_attachment=True,
            download_name=f"relatorio_desistencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype="application/pdf"
        )
        
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500

@relatorios.route('/exportar/<relatorio_tipo>', methods=['GET'])
@auth_required()
def exportar_relatorio(relatorio_tipo):
    """
    Exporta relatórios em formato CSV, Excel ou PDF
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
    parameters:
      - name: relatorio_tipo
        in: path
        type: string
        required: true
        description: Tipo de relatório (titulos, remessas, erros, desistencias, eficiencia, financeiro)
      - name: formato
        in: query
        type: string
        required: false
        description: Formato de exportação (csv, excel, pdf)
        default: csv
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
      - name: status
        in: query
        type: string
        required: false
        description: Status para filtrar (varia conforme o tipo de relatório)
    responses:
      200:
        description: Arquivo para download
      400:
        description: Parâmetros inválidos
      404:
        description: Tipo de relatório não encontrado
    """
    try:
        # Validar formato
        formato = request.args.get('formato', 'csv').lower()
        if formato not in ['csv', 'excel', 'pdf']:
            return jsonify({'error': f'Formato {formato} não suportado. Use csv, excel ou pdf.'}), 400
            
        # Obter dados conforme tipo de relatório
        if relatorio_tipo == 'titulos':
            dados = obter_dados_relatorio_titulos(request.args)
            filename = f"relatorio_titulos_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif relatorio_tipo == 'remessas':
            dados = obter_dados_relatorio_remessas(request.args)
            filename = f"relatorio_remessas_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif relatorio_tipo == 'erros':
            dados = obter_dados_relatorio_erros(request.args)
            filename = f"relatorio_erros_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif relatorio_tipo == 'desistencias':
            dados = obter_dados_relatorio_desistencias(request.args)
            filename = f"relatorio_desistencias_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif relatorio_tipo == 'eficiencia':
            # Obter dados do relatório de eficiência
            resultado = relatorio_eficiencia()
            if resultado.status_code != 200:
                return resultado
            dados = json.loads(resultado.data)['dados']
            filename = f"relatorio_eficiencia_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif relatorio_tipo == 'financeiro':
            # Verificar se o usuário é admin
            if not getattr(g.user, 'admin', False):
                return jsonify({'error': 'Acesso negado. Apenas administradores podem exportar relatórios financeiros.'}), 403
                
            # Obter dados do relatório financeiro
            resultado = relatorio_financeiro()
            if resultado.status_code != 200:
                return resultado
            dados = json.loads(resultado.data)['dados']
            filename = f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M')}"
        else:
            return jsonify({'error': f'Tipo de relatório {relatorio_tipo} não encontrado.'}), 404
            
        # Verificar se há dados
        if not dados:
            return jsonify({'error': 'Não foram encontrados dados para exportação com os filtros aplicados.'}), 404
            
        # Exportar no formato solicitado
        if formato == 'csv':
            return export_to_csv(dados, f"{filename}.csv")
        elif formato == 'excel':
            return export_to_excel(dados, f"{filename}.xlsx")
        elif formato == 'pdf':
            return export_to_pdf(dados, None, f"{filename}.pdf")
            
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar relatório: {str(e)}")
        return jsonify({'error': f'Erro ao exportar relatório: {str(e)}'}), 500

# Funções auxiliares para obter dados de relatórios
def obter_dados_relatorio_titulos(args):
    """Função auxiliar para obter dados de títulos para exportação"""
    status = args.get("status")
    data_inicio_str = args.get("data_inicio")
    data_fim_str = args.get("data_fim")
    
    # Construir query base
    query = Titulo.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Titulo.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao >= data_inicio)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
            query = query.filter(Titulo.data_emissao <= data_fim)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    # Executar query
    titulos = query.order_by(Titulo.data_cadastro.desc()).all()
    
    # Formatar dados para exportação
    dados_formatados = []
    for titulo in titulos:
        dados_formatados.append({
            "Número": titulo.numero,
            "Protocolo": titulo.protocolo,
            "Valor": float(titulo.valor) if titulo.valor else 0,
            "Data Emissão": titulo.data_emissao.strftime("%d/%m/%Y") if titulo.data_emissao else "N/A",
            "Data Vencimento": titulo.data_vencimento.strftime("%d/%m/%Y") if titulo.data_vencimento else "N/A",
            "Status": titulo.status,
            "Devedor": titulo.devedor.nome if titulo.devedor else "N/A",
            "Credor": titulo.credor.nome if titulo.credor else "N/A"
        })
    
    return dados_formatados

def obter_dados_relatorio_remessas(args):
    """Função auxiliar para obter dados de remessas para exportação"""
    status = args.get("status")
    data_inicio_str = args.get("data_inicio")
    data_fim_str = args.get("data_fim")
    
    # Construir query base
    query = Remessa.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Remessa.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Remessa.data_envio >= data_inicio)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Remessa.data_envio <= data_fim)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    # Executar query
    remessas = query.order_by(Remessa.data_envio.desc()).all()
    
    # Formatar dados para exportação
    dados_formatados = []
    for remessa in remessas:
        dados_formatados.append({
            "Nome Arquivo": remessa.nome_arquivo,
            "Data Envio": remessa.data_envio.strftime("%d/%m/%Y %H:%M") if remessa.data_envio else "N/A",
            "Status": remessa.status,
            "Tipo": remessa.tipo,
            "Quantidade Títulos": remessa.quantidade_titulos,
            "Títulos Processados": remessa.titulos.count(),
            "Erros": remessa.erros.count(),
            "Usuário": remessa.usuario.nome_completo if hasattr(remessa, "usuario") and remessa.usuario else "N/A",
            "Data Processamento": remessa.data_processamento.strftime("%d/%m/%Y %H:%M") if remessa.data_processamento else "N/A"
        })
    
    return dados_formatados

def obter_dados_relatorio_erros(args):
    """Função auxiliar para obter dados de erros para exportação"""
    tipo = args.get("tipo")
    resolvido_str = args.get("resolvido")
    data_inicio_str = args.get("data_inicio")
    data_fim_str = args.get("data_fim")
    
    # Construir query base
    query = Erro.query
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Erro.tipo == tipo)
    
    if resolvido_str is not None:
        resolvido = resolvido_str.lower() == "true"
        query = query.filter(Erro.resolvido == resolvido)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Erro.data_ocorrencia >= data_inicio)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Erro.data_ocorrencia <= data_fim)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    # Executar query
    erros = query.order_by(Erro.data_ocorrencia.desc()).all()
    
    # Formatar dados para exportação
    dados_formatados = []
    for erro in erros:
        dados_formatados.append({
            "ID": erro.id,
            "Tipo": erro.tipo,
            "Data Ocorrência": erro.data_ocorrencia.strftime("%d/%m/%Y %H:%M") if erro.data_ocorrencia else "N/A",
            "Mensagem": erro.mensagem,
            "Resolvido": "Sim" if erro.resolvido else "Não",
            "Data Resolução": erro.data_resolucao.strftime("%d/%m/%Y %H:%M") if erro.data_resolucao else "N/A",
            "Resolvido Por": erro.usuario_resolucao.nome_completo if erro.usuario_resolucao else "N/A",
            "Título": erro.titulo.numero if erro.titulo else "N/A",
            "Remessa": erro.remessa.nome_arquivo if erro.remessa else "N/A"
        })
    
    return dados_formatados

def obter_dados_relatorio_desistencias(args):
    """Função auxiliar para obter dados de desistências para exportação"""
    status = args.get("status")
    data_inicio_str = args.get("data_inicio")
    data_fim_str = args.get("data_fim")
    
    # Construir query base
    query = Desistencia.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Desistencia.status == status)
    
    # Filtro por data
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            query = query.filter(Desistencia.data_solicitacao >= data_inicio)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            query = query.filter(Desistencia.data_solicitacao <= data_fim)
        except ValueError:
            return []  # Retornar lista vazia em caso de erro
    
    # Executar query
    desistencias = query.order_by(Desistencia.data_solicitacao.desc()).all()
    
    # Formatar dados para exportação
    dados_formatados = []
    for desistencia in desistencias:
        dados_formatados.append({
            "ID": desistencia.id,
            "Data Solicitação": desistencia.data_solicitacao.strftime("%d/%m/%Y %H:%M") if desistencia.data_solicitacao else "N/A",
            "Título": desistencia.titulo.numero if desistencia.titulo else "N/A",
            "Protocolo": desistencia.titulo.protocolo if desistencia.titulo else "N/A",
            "Devedor": desistencia.titulo.devedor.nome if desistencia.titulo and desistencia.titulo.devedor else "N/A",
            "Valor": float(desistencia.titulo.valor) if desistencia.titulo and desistencia.titulo.valor else 0,
            "Motivo": desistencia.motivo,
            "Status": desistencia.status,
            "Data Processamento": desistencia.data_processamento.strftime("%d/%m/%Y %H:%M") if desistencia.data_processamento else "N/A",
            "Usuário": desistencia.usuario.nome_completo if desistencia.usuario else "N/A"
        })
    
    return dados_formatados

@relatorios.route('/eficiencia-processo', methods=['GET'])
@auth_required()
@cache_result(timeout=600)  # Cache por 10 minutos
@log_performance
def relatorio_eficiencia():
    """
    Relatório de eficiência do processo de protesto
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
        description: Estatísticas de eficiência do processo
    """


@relatorios.route('/financeiro', methods=['GET'])
@auth_required(admin_required=True)
@cache_result(timeout=600)  # Cache por 10 minutos
@log_performance
def relatorio_financeiro():
    """
    Relatório financeiro - requer permissão de admin
    ---
    tags:
      - Relatórios
    security:
      - BasicAuth: []
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
        description: Dados financeiros do sistema
      403:
        description: Acesso negado (apenas administradores)
    """
