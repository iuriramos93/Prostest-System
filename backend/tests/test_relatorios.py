import json
import pytest
from datetime import datetime, timedelta
from app import db

def test_get_relatorio_titulos(client, init_database, auth_headers):
    """Testa a geração de relatório de títulos"""
    headers = auth_headers(1)
    
    # Parâmetros para o relatório
    params = {
        'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Pendente',
        'formato': 'json'
    }
    
    response = client.get(
        '/api/relatorios/titulos',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    
    # Verificar se o conteúdo é JSON
    data = json.loads(response.data)
    assert 'titulos' in data
    assert isinstance(data['titulos'], list)
    
    # Testar formato PDF
    params['formato'] = 'pdf'
    response = client.get(
        '/api/relatorios/titulos',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert response.headers.get('Content-Disposition', '').startswith('attachment; filename=')

def test_get_relatorio_remessas(client, init_database, auth_headers):
    """Testa a geração de relatório de remessas"""
    headers = auth_headers(1)
    
    # Parâmetros para o relatório
    params = {
        'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Processado',
        'formato': 'json'
    }
    
    response = client.get(
        '/api/relatorios/remessas',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    
    # Verificar se o conteúdo é JSON
    data = json.loads(response.data)
    assert 'remessas' in data
    assert isinstance(data['remessas'], list)
    
    # Testar formato CSV
    params['formato'] = 'csv'
    response = client.get(
        '/api/relatorios/remessas',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.content_type == 'text/csv'
    assert response.headers.get('Content-Disposition', '').startswith('attachment; filename=')

def test_get_relatorio_erros(client, init_database, auth_headers):
    """Testa a geração de relatório de erros"""
    headers = auth_headers(1)
    
    # Parâmetros para o relatório
    params = {
        'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Pendente',
        'formato': 'json'
    }
    
    response = client.get(
        '/api/relatorios/erros',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    
    # Verificar se o conteúdo é JSON
    data = json.loads(response.data)
    assert 'erros' in data
    assert isinstance(data['erros'], list)
    
    # Testar formato Excel
    params['formato'] = 'excel'
    response = client.get(
        '/api/relatorios/erros',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.headers.get('Content-Disposition', '').startswith('attachment; filename=')

def test_get_relatorio_desistencias(client, init_database, auth_headers):
    """Testa a geração de relatório de desistências"""
    headers = auth_headers(1)
    
    # Parâmetros para o relatório
    params = {
        'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Aprovada',
        'formato': 'json'
    }
    
    response = client.get(
        '/api/relatorios/desistencias',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 200
    
    # Verificar se o conteúdo é JSON
    data = json.loads(response.data)
    assert 'desistencias' in data
    assert isinstance(data['desistencias'], list)

def test_get_relatorio_dashboard(client, init_database, auth_headers):
    """Testa a geração de relatório para o dashboard"""
    headers = auth_headers(1)
    
    response = client.get(
        '/api/relatorios/dashboard',
        headers=headers
    )
    
    assert response.status_code == 200
    
    # Verificar se o conteúdo é JSON com as estatísticas esperadas
    data = json.loads(response.data)
    assert 'total_titulos' in data
    assert 'titulos_por_status' in data
    assert 'remessas_recentes' in data
    assert 'erros_por_tipo' in data

def test_relatorio_parametros_invalidos(client, init_database, auth_headers):
    """Testa a validação de parâmetros inválidos nos relatórios"""
    headers = auth_headers(1)
    
    # Data em formato inválido
    params = {
        'data_inicio': 'data-invalida',
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'formato': 'json'
    }
    
    response = client.get(
        '/api/relatorios/titulos',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 400
    
    # Formato de saída inválido
    params = {
        'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'data_fim': datetime.now().strftime('%Y-%m-%d'),
        'formato': 'formato_invalido'
    }
    
    response = client.get(
        '/api/relatorios/titulos',
        query_string=params,
        headers=headers
    )
    
    assert response.status_code == 400