from datetime import datetime, timedelta
from io import BytesIO
from flask import request, jsonify, send_file, g
from app.auth.middleware import auth_required
from sqlalchemy import func, desc, and_, or_
from app import db
from app.models import Titulo, Remessa, Erro, Desistencia, User, Credor, Devedor
from . import relatorios

# Importações para geração de PDF
import pdfkit
import tempfile
import os

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
    html = "<h1>Relatório de Desistências</h1>"
    html += f"<p>Total de Desistências: {resumo['total_desistencias']}</p>"
    html += f"<p>Aprovadas: {resumo['aprovadas']}</p>"
    html += f"<p>Pendentes: {resumo['pendentes']}</p>"
    html += f"<p>Rejeitadas: {resumo['rejeitadas']}</p>"
    html += f"<p>Gerado em: {resumo['data_geracao']}</p>"
    html += "<table border=\"1\" style=\"width:100%; border-collapse: collapse;\">"
    html += "<tr><th>ID</th><th>Título</th><th>Protocolo</th><th>Devedor</th><th>Motivo</th><th>Status</th><th>Data Solicitação</th><th>Data Processamento</th><th>Usuário</th><th>Usuário Processamento</th></tr>"
    for desistencia in dados:
        html += f"<tr><td>{desistencia['id']}</td><td>{desistencia['titulo']}</td><td>{desistencia['protocolo']}</td><td>{desistencia['devedor']}</td><td>{desistencia['motivo']}</td><td>{desistencia['status']}</td><td>{desistencia['data_solicitacao']}</td><td>{desistencia['data_processamento']}</td><td>{desistencia['usuario']}</td><td>{desistencia['usuario_processamento']}</td></tr>"
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
            download_name="relatorio_desistencias.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar PDF: {str(e)}"}), 500
