#!/usr/bin/env python
"""
Script simplificado para testar a configuração CORS do backend
"""
import requests
import json

def test_cors():
    """Teste simples de CORS"""
    base_url = "http://localhost:5001"
    endpoints = [
        '/api/auth/login',
        '/api/remessas',
        '/api/titulos',
        '/api/desistencias',
        '/api/erros',
        '/api/relatorios'
    ]
    
    origin = "http://localhost:5173"
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        # Teste OPTIONS
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization, Content-Type'
        }
        
        print(f"\n\nTestando OPTIONS para {url}")
        try:
            response = requests.options(url, headers=headers, timeout=5)
            print(f"Status: {response.status_code}")
            print("Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Erro: {str(e)}")
        
        # Teste GET
        headers = {
            'Origin': origin,
            'Authorization': 'Basic YWRtaW46YWRtaW4xMjM='  # admin:admin123
        }
        
        print(f"\nTestando GET para {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {response.status_code}")
            print("Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            print("Resposta:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"Erro: {str(e)}")

if __name__ == "__main__":
    test_cors() 