# Configuração de Ambientes para o Sistema de Protesto

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações base compartilhadas por todos os ambientes
class Config:
    """Configuração base para todos os ambientes"""
    # Configurações gerais
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-nao-usar-em-producao'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-chave-secreta-padrao-nao-usar-em-producao'
    
    # Configurações de banco de dados
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Configurações de segurança
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 horas em segundos
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 dias em segundos
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    @staticmethod
    def init_app(app):
        """Inicialização da aplicação com configurações base"""
        # Criar diretório de uploads se não existir
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Criar diretório de logs se não existir
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        os.makedirs(log_dir, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:postgres@127.0.0.1:5432/protest_dev'
    
    # Desativar segurança de cookies em desenvolvimento
    JWT_COOKIE_SECURE = False
    
    # Configurações específicas para desenvolvimento
    SQLALCHEMY_ECHO = True  # Log de SQL
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configurações adicionais para desenvolvimento
        from flask_cors import CORS
        CORS(app, resources={r"/api/*": {"origins": "*"}})


class TestingConfig(Config):
    """Configuração para ambiente de testes"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:postgres@127.0.0.1:5432/protest_test'
    
    # Desativar segurança de cookies em testes
    JWT_COOKIE_SECURE = False
    
    # Configurações específicas para testes
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Configurações específicas para produção
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configurar manipuladores de erro de produção
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Configurar logger de arquivo
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # Adicionar handler ao logger da aplicação
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # Configurar CORS para produção
        from flask_cors import CORS
        CORS(app, resources={
            r"/api/*": {
                "origins": os.environ.get('ALLOWED_ORIGINS', 'https://protestsystem.com.br'),
                "supports_credentials": True
            }
        })


class StagingConfig(ProductionConfig):
    """Configuração para ambiente de homologação (staging)"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


# Mapeamento de configurações por ambiente
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}