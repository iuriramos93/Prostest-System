#!/usr/bin/env python
"""
Script para criar uma migração para adicionar o campo descricao ao modelo Remessa.
"""
import os
import sys
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from flask_migrate import Migrate, upgrade, migrate

def create_migration():
    """Cria uma migração para adicionar o campo descricao ao modelo Remessa."""
    print("Criando migração para adicionar o campo descricao ao modelo Remessa...")
    
    # Criar a aplicação Flask
    app = create_app()
    
    # Configurar o Migrate
    migrate_instance = Migrate(app, db)
    
    # Criar a migração
    with app.app_context():
        migrate()
        print("Migração criada com sucesso!")

if __name__ == "__main__":
    create_migration() 