#!/usr/bin/env python
"""
Script para testar a configuração CORS do backend
"""
import sys
import os
import requests
from urllib.parse import urljoin
import json
from colorama import init, Fore, Style

# Inicializar colorama para saída colorida no terminal
init()

# Adicionar diretório pai ao path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_header(message):
    """Imprime um cabeçalho formatado"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}" + "=" * 80)
    print(f" {message}")
    print("=" * 80 + f"{Style.RESET_ALL}\n")

def print_success(message):
    """Imprime uma mensagem de sucesso"""
    print(f"{Fore.GREEN}{Style.BRIGHT}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Imprime uma mensagem de erro"""
    print(f"{Fore.RED}{Style.BRIGHT}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Imprime uma mensagem informativa"""
    print(f"{Fore.BLUE}{Style.BRIGHT}ℹ {message}{Style.RESET_ALL}")

def test_options_request(base_url, endpoint, origin):
    """
    Testa uma requisição OPTIONS para verificar o comportamento CORS
    
    Args:
        base_url: URL base da API
        endpoint: Endpoint a ser testado
        origin: Origem da requisição (header Origin)
        
    Returns:
        True se o teste for bem-sucedido, False caso contrário
    """
    url = urljoin(base_url, endpoint)
    headers = {
        'Origin': origin,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Authorization, Content-Type'
    }
    
    try:
        response = requests.options(url, headers=headers)
        
        # Verificar status code
        if response.status_code != 200:
            print_error(f"Requisição OPTIONS para {endpoint} falhou com status {response.status_code}")
            return False
        
        # Verificar headers CORS
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Credentials'
        ]
        
        for header in cors_headers:
            if header not in response.headers:
                print_error(f"Header {header} não encontrado na resposta")
                return False
        
        # Verificar se a origem está correta
        if response.headers['Access-Control-Allow-Origin'] != origin:
            print_error(f"Access-Control-Allow-Origin esperado: {origin}, recebido: {response.headers['Access-Control-Allow-Origin']}")
            return False
        
        # Verificar se o header Authorization está permitido
        allowed_headers = response.headers['Access-Control-Allow-Headers']
        if 'authorization' not in allowed_headers.lower():
            print_error(f"Header Authorization não está permitido em Access-Control-Allow-Headers: {allowed_headers}")
            return False
        
        print_success(f"Requisição OPTIONS para {endpoint} bem-sucedida")
        return True
    
    except Exception as e:
        print_error(f"Erro ao fazer requisição OPTIONS para {endpoint}: {str(e)}")
        return False

def main():
    """Função principal"""
    print_header("Teste de Configuração CORS")
    
    # Configurações
    base_url = os.environ.get('API_URL', 'http://localhost:5001')
    origins = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]
    
    endpoints = [
        '/api/auth/login',
        '/api/remessas',
        '/api/titulos',
        '/api/desistencias',
        '/api/erros',
        '/api/relatorios'
    ]
    
    print_info(f"URL base da API: {base_url}")
    print_info(f"Origens a serem testadas: {', '.join(origins)}")
    print_info(f"Endpoints a serem testados: {', '.join(endpoints)}")
    
    # Testar cada combinação de origem e endpoint
    results = []
    
    for origin in origins:
        for endpoint in endpoints:
            result = test_options_request(base_url, endpoint, origin)
            results.append(result)
    
    # Resumo dos resultados
    success_count = results.count(True)
    total_tests = len(results)
    
    print_header("Resumo dos Resultados")
    print(f"Total de testes: {total_tests}")
    print(f"Testes bem-sucedidos: {success_count}")
    print(f"Testes falhos: {total_tests - success_count}")
    
    if success_count == total_tests:
        print_success("Todos os testes foram bem-sucedidos!")
        return 0
    else:
        print_error(f"{total_tests - success_count} testes falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 