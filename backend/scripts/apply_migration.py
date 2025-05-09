#!/usr/bin/env python
"""
Script para aplicar a migração para adicionar o campo descricao ao modelo Remessa.
"""
import os
import sys
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from flask_migrate import Migrate, upgrade

def apply_migration():
    """Aplica a migração para adicionar o campo descricao ao modelo Remessa."""
    print("Aplicando migração para adicionar o campo descricao ao modelo Remessa...")
    
    # Criar a aplicação Flask
    app = create_app()
    
    # Configurar o Migrate
    migrate_instance = Migrate(app, db)
    
    # Aplicar a migração
    with app.app_context():
        upgrade()
        print("Migração aplicada com sucesso!")

if __name__ == "__main__":
    apply_migration() 