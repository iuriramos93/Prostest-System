from datetime import datetime, timedelta
from flask import jsonify, request
from app.auth.middleware import auth_required
from sqlalchemy import func, and_, desc
from app import db
from app.models import Remessa, Titulo, Desistencia, Erro
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
      - JWT: []
    responses:
      200:
        description: Estatísticas resumidas
    """
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

@dashboard.route('/recent-submissions', methods=['GET'])
@auth_required()
def get_recent_submissions():
    """Retorna lista de remessas recentes com paginação e filtros
    ---
    tags:
      - Dashboard
    security:
      - JWT: []
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
            pass
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Adicionar um dia para incluir todo o dia final
            end_date = end_date + timedelta(days=1)
            query = query.filter(Remessa.data_envio < end_date)
        except ValueError:
            pass
    
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

@dashboard.route('/status-distribution', methods=['GET'])
@auth_required()
def get_status_distribution():
    """Retorna distribuição de status dos títulos e tendência dos últimos 30 dias
    ---
    tags:
      - Dashboard
    security:
      - JWT: []
    responses:
      200:
        description: Distribuição de status e tendência
    """
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