# Utilitários de performance para o Sistema de Protesto

from functools import wraps
from datetime import datetime
from flask import request, current_app
import hashlib
import json

# Cache em memória global - em produção, deveria ser substituído por Redis ou similar
_cache = {}

def cache_result(timeout=300):
    """
    Decorator para cache de resultados de funções e endpoints
    
    Args:
        timeout: Tempo de vida do cache em segundos (padrão: 5 minutos)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gera uma chave única baseada na função e seus argumentos
            cache_key = _generate_cache_key(f.__name__, args, kwargs, request.args)
            
            # Verifica se a requisição solicita ignorar o cache
            if request.args.get('no_cache') == 'true':
                result = f(*args, **kwargs)
                _cache[cache_key] = {
                    'data': result,
                    'timestamp': datetime.utcnow().timestamp()
                }
                return result
            
            # Verifica se há cache válido
            if cache_key in _cache:
                timestamp = _cache[cache_key]['timestamp']
                now = datetime.utcnow().timestamp()
                
                # Verifica se o cache ainda é válido
                if now - timestamp < timeout:
                    current_app.logger.debug(f"Cache hit para {f.__name__} com chave {cache_key}")
                    return _cache[cache_key]['data']
                
                current_app.logger.debug(f"Cache expirado para {f.__name__} com chave {cache_key}")
            else:
                current_app.logger.debug(f"Cache miss para {f.__name__} com chave {cache_key}")
            
            # Executa a função e armazena o resultado no cache
            result = f(*args, **kwargs)
            _cache[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow().timestamp()
            }
            return result
        return decorated_function
    return decorator

def _generate_cache_key(func_name, args, kwargs, request_args):
    """
    Gera uma chave única para o cache baseada na função e seus argumentos
    
    Args:
        func_name: Nome da função
        args: Argumentos posicionais
        kwargs: Argumentos nomeados
        request_args: Argumentos da requisição HTTP
        
    Returns:
        str: Chave única para o cache
    """
    # Converter argumentos da requisição para uma string ordenada
    req_args_str = ""
    if request_args:
        # Ordenar para garantir consistência
        sorted_args = sorted(request_args.items())
        # Ignorar parâmetros que não afetam o resultado (como no_cache)
        filtered_args = [(k, v) for k, v in sorted_args if k != 'no_cache']
        req_args_str = json.dumps(filtered_args)
    
    # Construir uma string com todos os argumentos
    key_parts = [func_name, str(args), str(kwargs), req_args_str]
    key_string = "|".join(key_parts)
    
    # Usar hash para reduzir o tamanho da chave
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()

def clear_cache(key_prefix=None):
    """
    Limpa o cache, opcionalmente apenas para chaves com um prefixo específico
    
    Args:
        key_prefix: Prefixo das chaves a serem removidas (opcional)
    """
    global _cache
    
    if key_prefix is None:
        # Limpa todo o cache
        _cache = {}
        current_app.logger.info("Cache completo foi limpo")
    else:
        # Limpa apenas as chaves que começam com o prefixo
        keys_to_remove = [k for k in _cache.keys() if k.startswith(key_prefix)]
        for k in keys_to_remove:
            del _cache[k]
        current_app.logger.info(f"Cache com prefixo '{key_prefix}' foi limpo ({len(keys_to_remove)} entradas)")

def log_performance(f):
    """
    Decorator para registrar o tempo de execução de uma função
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import time
        
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Registrar tempo de execução
        current_app.logger.info(f"Função {f.__name__} executada em {execution_time:.4f} segundos")
        
        # Se o tempo de execução for alto, registrar um aviso
        if execution_time > 1.0:
            current_app.logger.warning(f"Performance crítica: {f.__name__} levou {execution_time:.4f} segundos")
            
            # Em produção, poderia enviar notificação ou alertas
        
        return result
    return decorated_function

def init_performance_tools(app):
    """
    Inicializa ferramentas de performance para a aplicação
    """
    # Configurar logging de performance
    import logging
    performance_logger = logging.getLogger('performance')
    performance_logger.setLevel(logging.INFO)
    
    # Adicionar handler para arquivo de log
    import os
    log_folder = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_folder, exist_ok=True)
    
    file_handler = logging.FileHandler(os.path.join(log_folder, 'performance.log'))
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    performance_logger.addHandler(file_handler)
    
    @app.after_request
    def add_cache_headers(response):
        # Adiciona cache para recursos estáticos
        if request.path.startswith('/static'):
            response.cache_control.max_age = 86400  # 24 horas
            response.cache_control.public = True
        return response