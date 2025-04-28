# Utilitários de performance para o Sistema de Protesto

from functools import wraps
import time
import logging
from flask import request, current_app
from flask_caching import SimpleCache

# Cache em memória para dados frequentemente acessados
cache = SimpleCache()

def cache_result(timeout=300):
    """Decorator para cache de resultados de funções
    
    Args:
        timeout: Tempo em segundos para expiração do cache (padrão: 5 minutos)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gera uma chave única baseada na função e seus argumentos
            cache_key = f.__name__ + str(args) + str(sorted(kwargs.items()))
            
            # Tenta obter resultado do cache
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            
            # Se não estiver em cache, executa a função
            rv = f(*args, **kwargs)
            
            # Armazena o resultado no cache
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def clear_cache(key_prefix=None):
    """Limpa o cache com o prefixo especificado
    
    Args:
        key_prefix: Prefixo da chave para limpar cache seletivamente
    """
    if key_prefix:
        # Implementação simplificada - em produção, use Redis para limpeza seletiva
        cache.clear()
    else:
        cache.clear()

def log_performance(f):
    """Decorator para registrar o tempo de execução de funções"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Registra o tempo de execução
        logging.info(
            f'Performance: {f.__name__} executada em {execution_time:.4f}s - '
            f'Endpoint: {request.endpoint}, Método: {request.method}, '
            f'IP: {request.remote_addr}'
        )
        
        # Alerta se o tempo de execução for muito alto
        if execution_time > 1.0:  # Alerta para funções que demoram mais de 1 segundo
            logging.warning(
                f'Performance crítica: {f.__name__} demorou {execution_time:.4f}s - '
                f'Endpoint: {request.endpoint}'
            )
            
        return result
    return decorated_function

def init_performance_tools(app):
    """Inicializa as ferramentas de performance no aplicativo Flask"""
    # Configurar compressão se Flask-Compress estiver disponível
    try:
        from flask_compress import Compress
        compress = Compress()
        compress.init_app(app)
        app.logger.info('Compressão gzip habilitada')
    except ImportError:
        app.logger.warning('Flask-Compress não encontrado. Compressão desabilitada.')
    
    # Configurar cache headers para recursos estáticos
    @app.after_request
    def add_cache_headers(response):
        # Adiciona cache para recursos estáticos
        if request.path.startswith('/static/'):
            # Cache por 1 semana para recursos estáticos
            response.cache_control.max_age = 604800
            response.cache_control.public = True
        return response
    
    app.logger.info('Ferramentas de performance inicializadas')
    
    return app