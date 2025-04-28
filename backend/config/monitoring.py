# Configuração de Monitoramento e Logging para o Sistema de Protesto

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
import time
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from prometheus_flask_exporter import PrometheusMetrics

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'app_request_count', 
    'Contador de requisições HTTP', 
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 
    'Latência das requisições HTTP', 
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'app_active_requests', 
    'Número de requisições ativas'
)

DB_QUERY_LATENCY = Histogram(
    'app_db_query_latency_seconds', 
    'Latência das consultas ao banco de dados', 
    ['query_type']
)

# Configuração de Logging
def configure_logging(app: Flask):
    """Configura o sistema de logging da aplicação"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configurar formato do log
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Configurar handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level))
    
    # Adicionar handler ao logger da aplicação
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, log_level))
    
    # Configurar log para bibliotecas externas
    for logger_name in ['sqlalchemy', 'werkzeug']:
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)
        logger.setLevel(getattr(logging, log_level))

# Configuração de Métricas Prometheus
def configure_metrics(app: Flask):
    """Configura métricas Prometheus para a aplicação"""
    metrics = PrometheusMetrics(app)
    
    # Métricas por endpoint
    metrics.info('app_info', 'Informações da aplicação', version='1.0.0')
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
        ACTIVE_REQUESTS.inc()
    
    @app.after_request
    def after_request(response):
        request_latency = time.time() - request.start_time
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.endpoint or 'unknown'
        ).observe(request_latency)
        
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.endpoint or 'unknown', 
            status=response.status_code
        ).inc()
        
        ACTIVE_REQUESTS.dec()
        
        return response
    
    # Endpoint para métricas
    @app.route('/metrics')
    def metrics():
        return prometheus_client.generate_latest()

# Função para medir tempo de consultas ao banco de dados
def measure_db_query(query_type, func, *args, **kwargs):
    """Decorator para medir o tempo de consultas ao banco de dados"""
    start_time = time.time()
    result = func(*args, **kwargs)
    query_time = time.time() - start_time
    DB_QUERY_LATENCY.labels(query_type=query_type).observe(query_time)
    return result

# Configuração de Health Check
def configure_health_check(app: Flask):
    """Configura endpoint de health check"""
    @app.route('/health')
    def health_check():
        # Verificar conexão com banco de dados
        try:
            from app import db
            db.session.execute('SELECT 1')
            db_status = 'ok'
        except Exception as e:
            app.logger.error(f"Erro na verificação do banco de dados: {str(e)}")
            db_status = 'error'
        
        # Verificar espaço em disco
        try:
            disk = os.statvfs('/')
            free_space = disk.f_bavail * disk.f_frsize
            total_space = disk.f_blocks * disk.f_frsize
            disk_usage = (total_space - free_space) / total_space * 100
            disk_status = 'ok' if disk_usage < 90 else 'warning'
        except Exception as e:
            app.logger.error(f"Erro na verificação de disco: {str(e)}")
            disk_status = 'unknown'
        
        # Verificar memória
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_status = 'ok' if memory.percent < 90 else 'warning'
        except ImportError:
            memory_status = 'unknown'
        except Exception as e:
            app.logger.error(f"Erro na verificação de memória: {str(e)}")
            memory_status = 'error'
        
        status = 'ok' if all(s == 'ok' for s in [db_status, disk_status, memory_status]) else 'degraded'
        
        return {
            'status': status,
            'timestamp': time.time(),
            'components': {
                'database': db_status,
                'disk': disk_status,
                'memory': memory_status
            }
        }

# Função principal para configurar monitoramento
def setup_monitoring(app: Flask):
    """Configura todo o sistema de monitoramento e logging"""
    configure_logging(app)
    configure_metrics(app)
    configure_health_check(app)
    
    app.logger.info('Sistema de monitoramento configurado com sucesso')