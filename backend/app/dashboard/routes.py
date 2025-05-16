from datetime import datetime, timedelta
from flask import jsonify, request, current_app
from app.auth.middleware import auth_required
from sqlalchemy import func, and_, desc, case
from app import db
from app.models import Remessa, Titulo, Desistencia, Erro, User, Devedor
from . import dashboard

# Cache simples em memória com expiração
_cache = {}

# Função auxiliar para criar cache key baseado nos parâmetros da requisição
def _get_cache_key(prefix, **kwargs):
    """Gera uma chave de cache baseada no prefixo e parâmetros"""
    key = prefix
    for k, v in sorted(kwargs.items()):
        key += f":{k}={v}"
    return key

def _get_cached_data(key, ttl=300):
    """Obtém dados do cache se existirem e não estiverem expirados
    
    Args:
        key: Chave do cache
        ttl: Tempo de vida em segundos (padrão: 5 minutos)
        
    Returns:
        Dados em cache ou None se não existirem ou estiverem expirados
    """
    if key in _cache:
        timestamp, data = _cache[key]
        if datetime.utcnow().timestamp() - timestamp < ttl:
            return data
    return None

def _set_cache_data(key, data):
    """Armazena dados no cache
    
    Args:
        key: Chave do cache
        data: Dados a serem armazenados
    """
    _cache[key] = (datetime.utcnow().timestamp(), data)

@dashboard.route('/summary', methods=['GET'])
@auth_required()
def get_summary_statistics():
    """Retorna estatísticas resumidas do sistema
    ---
    tags:
      - Dashboard
    security:
      - BasicAuth: []
    responses:
      200:
        description: Estatísticas resumidas
    """
    try:
        # Verificar se há dados em cache
        cache_key = _get_cache_key('dashboard_summary')
        cached_data = _get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Consultas para estatísticas
        total_remessas = Remessa.query.count()
        total_titulos = Titulo.query.count()
        total_desistencias = Desistencia.query.count()
        total_erros = Erro.query.count()
        erros_nao_resolvidos = Erro.query.filter_by(resolvido=False).count()
        
        # Estatísticas por status de título
        titulos_por_status = db.session.query(
            Titulo.status, func.count(Titulo.id)
        ).group_by(Titulo.status).all()
        
        status_counts = {status: count for status, count in titulos_por_status}
        
        # Construir resposta
        response = {
            'total_remessas': total_remessas,
            'total_titulos': total_titulos,
            'total_desistencias': total_desistencias,
            'erros': {
                'total': total_erros,
                'nao_resolvidos': erros_nao_resolvidos
            },
            'titulos_por_status': status_counts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Armazenar no cache
        _set_cache_data(cache_key, response)
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas resumidas: {str(e)}")
        return jsonify({'error': f'Erro ao processar solicitação: {str(e)}'}), 500

@dashboard.route('/recent-submissions', methods=['GET'])
@auth_required()
def get_recent_submissions():
    """Retorna lista de remessas recentes com paginação e filtros
    ---
    tags:
      - Dashboard
    security:
      - BasicAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 10
      - name: status
        in: query
        type: string
        description: Filtrar por status (Processado, Pendente, Erro)
      - name: tipo
        in: query
        type: string
        description: Filtrar por tipo (Remessa, Confirmação, Retorno)
      - name: start_date
        in: query
        type: string
        format: date
        description: Data inicial (YYYY-MM-DD)
      - name: end_date
        in: query
        type: string
        format: date
        description: Data final (YYYY-MM-DD)
    responses:
      200:
        description: Lista de remessas recentes
    """
    try:
        # Parâmetros de paginação e filtro
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Limitar a 100 itens por página
        status = request.args.get('status')
        tipo = request.args.get('tipo')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Criar chave de cache baseada nos parâmetros
        cache_key = _get_cache_key('recent_submissions', 
                                page=page, 
                                per_page=per_page, 
                                status=status, 
                                tipo=tipo, 
                                start_date=start_date, 
                                end_date=end_date)
        
        # Verificar cache
        cached_data = _get_cached_data(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        # Construir query base
        query = Remessa.query
        
        # Aplicar filtros
        if status:
            query = query.filter(Remessa.status == status)
        if tipo:
            query = query.filter(Remessa.tipo == tipo)
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Remessa.data_envio >= start_date)
            except ValueError:
                return jsonify({"error": "Formato de data inválido para start_date. Use YYYY-MM-DD"}), 400
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # Adicionar um dia para incluir todo o dia final
                end_date = end_date + timedelta(days=1)
                query = query.filter(Remessa.data_envio < end_date)
            except ValueError:
                return jsonify({"error": "Formato de data inválido para end_date. Use YYYY-MM-DD"}), 400
        
        # Ordenar por data de envio (mais recente primeiro)
        query = query.order_by(desc(Remessa.data_envio))
        
        # Executar consulta paginada
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        remessas = pagination.items
        
        # Preparar resposta
        response = {
            'items': [remessa.to_dict() for remessa in remessas],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
        
        # Armazenar no cache
        _set_cache_data(cache_key, response)
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Erro ao obter remessas recentes: {str(e)}")
        return jsonify({'error': f'Erro ao processar solicitação: {str(e)}'}), 500

@dashboard.route('/status-distribution', methods=['GET'])
@auth_required()
def get_status_distribution():
    """Retorna distribuição de status dos títulos e tendência dos últimos 30 dias
    ---
    tags:
      - Dashboard
    security:
      - BasicAuth: []
    responses:
      200:
        description: Distribuição de status e tendência
    """
    try:
        # Verificar cache
        cache_key = _get_cache_key('status_distribution')
        cached_data = _get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Distribuição atual de status
        status_distribution = db.session.query(
            Titulo.status, func.count(Titulo.id)
        ).group_by(Titulo.status).all()
        
        # Converter para dicionário
        current_distribution = {status: count for status, count in status_distribution}
        
        # Calcular tendência dos últimos 30 dias
        today = datetime.utcnow().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Consulta para obter contagem diária por status nos últimos 30 dias
        daily_trends = {}
        
        # Para cada dia nos últimos 30 dias
        for days_ago in range(30, -1, -1):
            date = today - timedelta(days=days_ago)
            next_date = date + timedelta(days=1)
            
            # Consulta para este dia específico
            day_data = db.session.query(
                Titulo.status, func.count(Titulo.id)
            ).filter(
                func.date(Titulo.data_cadastro) == date
            ).group_by(Titulo.status).all()
            
            # Formatar data como string YYYY-MM-DD
            date_str = date.strftime('%Y-%m-%d')
            daily_trends[date_str] = {status: count for status, count in day_data}
        
        # Construir resposta
        response = {
            'current_distribution': current_distribution,
            'daily_trends': daily_trends
        }
        
        # Armazenar no cache
        _set_cache_data(cache_key, response)
        
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Erro ao obter distribuição de status: {str(e)}")
        return jsonify({'error': f'Erro ao processar solicitação: {str(e)}'}), 500

@dashboard.route('/estatisticas-gerais', methods=['GET'])
@auth_required()
def get_estatisticas_gerais():
    """Endpoint que retorna estatísticas gerais do sistema agregadas por mês
    ---
    tags:
      - Dashboard
    security:
      - BasicAuth: []
    responses:
      200:
        description: Estatísticas gerais do sistema
    """
    try:
        # Verificar cache
        cache_key = _get_cache_key('estatisticas_gerais')
        cached_data = _get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Estatísticas de títulos por mês
        titulos_por_mes = db.session.query(
            func.date_trunc('month', Titulo.data_cadastro).label('mes'),
            func.count().label('quantidade'),
            func.sum(Titulo.valor).label('valor_total')
        ).group_by('mes').order_by('mes').all()
        
        # Estatísticas de protestos por mês
        protestos_por_mes = db.session.query(
            func.date_trunc('month', Titulo.data_protesto).label('mes'),
            func.count().label('quantidade'),
            func.sum(Titulo.valor).label('valor_total')
        ).filter(Titulo.status == 'Protestado').group_by('mes').order_by('mes').all()
        
        # Estatísticas de desistências por mês
        desistencias_por_mes = db.session.query(
            func.date_trunc('month', Desistencia.data_solicitacao).label('mes'),
            func.count().label('quantidade')
        ).group_by('mes').order_by('mes').all()
        
        # Formatação dos resultados
        resultado = {
            'titulos_por_mes': [{'mes': r[0].strftime('%Y-%m'), 'quantidade': r[1], 'valor_total': float(r[2] or 0)} for r in titulos_por_mes],
            'protestos_por_mes': [{'mes': r[0].strftime('%Y-%m'), 'quantidade': r[1], 'valor_total': float(r[2] or 0)} for r in protestos_por_mes],
            'desistencias_por_mes': [{'mes': r[0].strftime('%Y-%m'), 'quantidade': r[1]} for r in desistencias_por_mes]
        }
        
        # Armazenar no cache
        _set_cache_data(cache_key, resultado)
        
        return jsonify(resultado)
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas gerais: {str(e)}")
        return jsonify({'error': f'Erro ao processar solicitação: {str(e)}'}), 500

@dashboard.route('/totais-por-status', methods=['GET'])
@auth_required()
def get_totais_por_status():
    """Endpoint que retorna o total de títulos por status
    ---
    tags:
      - Dashboard
    security:
      - BasicAuth: []
    responses:
      200:
        description: Total de títulos por status
    """
    try:
        # Verificar cache
        cache_key = _get_cache_key('totais_por_status')
        cached_data = _get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)
        
        # Estatísticas de títulos por status
        titulos_por_status = db.session.query(
            Titulo.status,
            func.count().label('quantidade'),
            func.sum(Titulo.valor).label('valor_total')
        ).group_by(Titulo.status).all()
        
        # Formatação do resultado
        resultado = {
            'totais_por_status': [
                {
                    'status': r[0], 
                    'quantidade': r[1], 
                    'valor_total': float(r[2] or 0)
                } for r in titulos_por_status
            ]
        }
        
        # Armazenar no cache
        _set_cache_data(cache_key, resultado)
        
        return jsonify(resultado)
    except Exception as e:
        current_app.logger.error(f"Erro ao obter totais por status: {str(e)}")
        return jsonify({'error': f'Erro ao processar solicitação: {str(e)}'}), 500
