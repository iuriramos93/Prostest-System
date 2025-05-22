from flask import Blueprint

# Importar todos os módulos da API v1
from app.api.v1.titulos import register_api_v1 as register_titulos_api
from app.api.v1.users import register_api_v1_users as register_users_api

def register_api(app):
    """
    Registra todos os endpoints da API versionada
    """
    # Registrar API v1
    register_titulos_api(app)
    register_users_api(app)
    
    # Aqui podem ser registradas futuras versões da API (v2, v3, etc.)
