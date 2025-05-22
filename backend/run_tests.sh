#!/bin/bash

# Script para executar testes de integração da API

echo "Iniciando testes de integração da API..."

# Configurar ambiente de teste
export FLASK_ENV=testing
export TESTING=True
export DATABASE_URL=postgresql://postgres:postgres@db:5432/protest_system_test

# Criar banco de dados de teste
echo "Criando banco de dados de teste..."
python -c "from app import create_app, db; app = create_app('testing'); app.app_context().push(); db.create_all()"

# Executar testes
echo "Executando testes de integração..."
python -m unittest discover -s tests

# Limpar banco de dados de teste
echo "Limpando banco de dados de teste..."
python -c "from app import create_app, db; app = create_app('testing'); app.app_context().push(); db.drop_all()"

echo "Testes de integração concluídos!"
