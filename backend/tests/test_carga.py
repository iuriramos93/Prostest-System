import time
import pytest
import json
import concurrent.futures
from datetime import datetime

"""
Testes de carga para validar as melhorias de performance descritas no README_PERFORMANCE.md

Este arquivo contém testes de carga que podem ser executados para validar as melhorias
de performance implementadas no sistema. Os testes utilizam múltiplas threads para
simular acessos concorrentes e medem o tempo de resposta das APIs.

Para executar apenas os testes de carga:
    python -m pytest tests/test_carga.py -v
"""

@pytest.mark.carga
def test_carga_listagem_titulos(client, init_database, auth_headers):
    """
    Teste de carga para a listagem de títulos.
    Simula múltiplos acessos concorrentes à API de listagem de títulos.
    """
    headers = auth_headers(1)
    num_requests = 50  # Número de requisições concorrentes
    
    def fazer_requisicao():
        return client.get('/api/titulos/', headers=headers)
    
    # Medir tempo total para executar todas as requisições
    start_time = time.time()
    
    # Executar requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fazer_requisicao) for _ in range(num_requests)]
        resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    tempo_total = end_time - start_time
    tempo_medio = tempo_total / num_requests
    
    # Verificar se todas as requisições foram bem-sucedidas
    assert all(response.status_code == 200 for response in resultados)
    
    # Verificar se o tempo médio está dentro do limite aceitável
    # Ajuste este valor conforme necessário com base nas expectativas de performance
    assert tempo_medio < 0.5, f"Tempo médio de resposta ({tempo_medio:.2f}s) excede o limite aceitável"
    
    print(f"\nTeste de carga para listagem de títulos:")
    print(f"Número de requisições: {num_requests}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo médio por requisição: {tempo_medio:.2f}s")


@pytest.mark.carga
def test_carga_listagem_protestos(client, init_database, auth_headers):
    """
    Teste de carga para a listagem de protestos.
    Simula múltiplos acessos concorrentes à API de listagem de protestos.
    """
    headers = auth_headers(1)
    num_requests = 50  # Número de requisições concorrentes
    
    # Preparar dados de teste - garantir que existam protestos
    with client.application.app_context():
        from app.models import Titulo, db
        titulos = Titulo.query.limit(5).all()
        for titulo in titulos:
            titulo.status = 'Protestado'
            titulo.data_protesto = datetime.now().date()
        db.session.commit()
    
    def fazer_requisicao():
        return client.get('/api/protestos/', headers=headers)
    
    # Medir tempo total para executar todas as requisições
    start_time = time.time()
    
    # Executar requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fazer_requisicao) for _ in range(num_requests)]
        resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    tempo_total = end_time - start_time
    tempo_medio = tempo_total / num_requests
    
    # Verificar se todas as requisições foram bem-sucedidas
    assert all(response.status_code == 200 for response in resultados)
    
    # Verificar se o tempo médio está dentro do limite aceitável
    assert tempo_medio < 0.5, f"Tempo médio de resposta ({tempo_medio:.2f}s) excede o limite aceitável"
    
    print(f"\nTeste de carga para listagem de protestos:")
    print(f"Número de requisições: {num_requests}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo médio por requisição: {tempo_medio:.2f}s")


@pytest.mark.carga
def test_carga_busca_titulos(client, init_database, auth_headers):
    """
    Teste de carga para busca de títulos com filtros.
    Simula múltiplos acessos concorrentes à API de busca de títulos.
    """
    headers = auth_headers(1)
    num_requests = 30  # Número de requisições concorrentes
    
    def fazer_requisicao():
        # Alternar entre diferentes filtros para simular uso real
        filtros = [
            '/api/titulos/?status=Pendente',
            '/api/titulos/?status=Protestado',
            '/api/titulos/?per_page=50'
        ]
        import random
        filtro = random.choice(filtros)
        return client.get(filtro, headers=headers)
    
    # Medir tempo total para executar todas as requisições
    start_time = time.time()
    
    # Executar requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fazer_requisicao) for _ in range(num_requests)]
        resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    tempo_total = end_time - start_time
    tempo_medio = tempo_total / num_requests
    
    # Verificar se todas as requisições foram bem-sucedidas
    assert all(response.status_code == 200 for response in resultados)
    
    # Verificar se o tempo médio está dentro do limite aceitável
    assert tempo_medio < 0.6, f"Tempo médio de resposta ({tempo_medio:.2f}s) excede o limite aceitável"
    
    print(f"\nTeste de carga para busca de títulos:")
    print(f"Número de requisições: {num_requests}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo médio por requisição: {tempo_medio:.2f}s")


@pytest.mark.carga
def test_carga_endpoints_agregados(client, init_database, auth_headers):
    """
    Teste de carga para endpoints agregados.
    Valida a performance dos endpoints que retornam dados compostos.
    """
    headers = auth_headers(1)
    num_requests = 20  # Número de requisições concorrentes
    
    # Preparar dados de teste se necessário
    with client.application.app_context():
        from app.models import Titulo, db
        titulo = Titulo.query.first()
        if titulo:
            titulo_id = titulo.id
        else:
            titulo_id = 1  # Fallback
    
    def fazer_requisicao():
        # Endpoint que retorna dados agregados (título com devedor, credor e remessa)
        return client.get(f'/api/titulos/{titulo_id}/completo', headers=headers)
    
    # Medir tempo total para executar todas as requisições
    start_time = time.time()
    
    # Executar requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fazer_requisicao) for _ in range(num_requests)]
        resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    tempo_total = end_time - start_time
    tempo_medio = tempo_total / num_requests
    
    # Verificar se todas as requisições foram bem-sucedidas (pode ser 200 ou 404 dependendo dos dados)
    assert all(response.status_code in [200, 404] for response in resultados)
    
    # Verificar se o tempo médio está dentro do limite aceitável
    assert tempo_medio < 0.3, f"Tempo médio de resposta ({tempo_medio:.2f}s) excede o limite aceitável"
    
    print(f"\nTeste de carga para endpoints agregados:")
    print(f"Número de requisições: {num_requests}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo médio por requisição: {tempo_medio:.2f}s")