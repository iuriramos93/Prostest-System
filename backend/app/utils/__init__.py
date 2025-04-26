# Pacote de utilitários para o Sistema de Protesto

from .email import send_email, send_template_email, EmailSender
from .performance import cache_result, clear_cache, log_performance, init_performance_tools

__all__ = [
    'send_email', 'send_template_email', 'EmailSender',
    'cache_result', 'clear_cache', 'log_performance', 'init_performance_tools'
]