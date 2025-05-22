#!/usr/bin/env python
"""
Script para iniciar o servidor Flask com a configuração CORS correta
"""
import os
import sys
from app import create_app
from flask import Flask
from flask_cors import CORS
from config.cors import configure_cors
from app.utils.middleware import register_middlewares

def create_test_app():
    """
    Cria uma aplicação Flask com configurações específicas para teste
    """
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    
    # Lista de origens permitidas para CORS
    app.config['CORS_ALLOWED_ORIGINS'] = [
        "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
        "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta padrão
        "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta alternativa
        "http://localhost:3000", "http://127.0.0.1:3000",  # Porta alternativa React
        "http://localhost:8080", "http://127.0.0.1:8080",  # Porta alternativa Vue/outros
    ]
    
    # Registrar middlewares
    register_middlewares(app)
    
    # Configuração CORS centralizada
    configure_cors(app)
    
    # Rota de teste
    @app.route('/test')
    def test():
        return {'message': 'API de teste funcionando!'}
    
    @app.route('/api/auth/login', methods=['GET', 'POST', 'OPTIONS'])
    def login():
        return {'message': 'Login endpoint de teste'}
    
    @app.route('/api/remessas', methods=['GET', 'POST', 'OPTIONS'])
    def remessas():
        return {'message': 'Remessas endpoint de teste'}
    
    @app.route('/api/titulos', methods=['GET', 'POST', 'OPTIONS'])
    def titulos():
        return {'message': 'Títulos endpoint de teste'}
    
    @app.route('/api/desistencias', methods=['GET', 'POST', 'OPTIONS'])
    def desistencias():
        return {'message': 'Desistências endpoint de teste'}
    
    @app.route('/api/erros', methods=['GET', 'POST', 'OPTIONS'])
    def erros():
        return {'message': 'Erros endpoint de teste'}
    
    @app.route('/api/relatorios', methods=['GET', 'POST', 'OPTIONS'])
    def relatorios():
        return {'message': 'Relatórios endpoint de teste'}
    
    return app

if __name__ == '__main__':
    # Verificar se é para iniciar a aplicação de teste
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        app = create_test_app()
    else:
        app = create_app('development')
    
    # Definir porta
    port = int(os.environ.get('PORT', 5001))
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=port, debug=True) 