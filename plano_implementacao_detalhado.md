# Plano de Implementação para Integração com Banco de Dados e Correção de Erros

## 1. Análise do Problema

Após analisar os scripts SQL e os logs de erro, identifiquei os seguintes problemas:

1. **Erro de Schema do Banco de Dados**: 
   - A coluna `task_id` está definida no modelo `Remessa` mas não existe na tabela `remessas` do banco de dados
   - Existe um commit específico para adicionar esta coluna, mas a migração não foi aplicada corretamente

2. **Problemas de CORS**:
   - Erros de CORS em múltiplos endpoints
   - Mensagem específica: "Response to preflight request doesn't pass access control check: Redirect is not allowed for a preflight request"

3. **Integração com Banco de Dados**:
   - As seções do frontend não estão exibindo dados reais do banco de dados PostgreSQL
   - Necessidade de garantir que todos os endpoints consultem as tabelas reais

## 2. Solução Proposta

### 2.1 Correção do Schema do Banco

1. **Adicionar a coluna `task_id` à tabela `remessas`**:
   ```sql
   ALTER TABLE remessas ADD COLUMN IF NOT EXISTS task_id VARCHAR(50);
   ```

2. **Garantir que o modelo `Remessa` esteja alinhado com o schema do banco**:
   - Verificar se todos os campos do modelo estão presentes na tabela
   - Ajustar tipos de dados se necessário

### 2.2 Correção dos Problemas de CORS

1. **Implementar uma configuração CORS robusta**:
   ```python
   # Configuração CORS centralizada
   allowed_origins = [
       "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
       "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta padrão
       "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta alternativa
   ]
   
   CORS(app, 
        origins=allowed_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Content-Type", "Authorization"])
   ```

2. **Implementar um handler OPTIONS robusto**:
   ```python
   @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
   @app.route('/<path:path>', methods=['OPTIONS'])
   def options_handler(path):
       response = make_response()
       response.status_code = 200
       origin = request.headers.get('Origin')
       if origin in allowed_origins:
           response.headers['Access-Control-Allow-Origin'] = origin
           response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
           response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
           response.headers['Access-Control-Allow-Credentials'] = 'true'
           response.headers['Access-Control-Max-Age'] = '3600'
       return response, 200
   ```

### 2.3 Integração com Banco de Dados

1. **Otimizar as consultas para cada seção**:
   - Implementar paginação eficiente
   - Utilizar índices adequados
   - Implementar cache para consultas frequentes

2. **Adaptar os endpoints para consultar o banco real**:
   - Remover dados simulados
   - Implementar queries otimizadas
   - Adicionar tratamento de erros robusto

## 3. Implementação Detalhada

### 3.1 Correção do Schema do Banco

```python
# Script para adicionar a coluna task_id
import psycopg2
from psycopg2 import sql

def add_task_id_column():
    conn = psycopg2.connect(
        dbname="protest_system",
        user="postgres",
        password="postgres",
        host="db",
        port="5432"
    )
    
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("ALTER TABLE remessas ADD COLUMN IF NOT EXISTS task_id VARCHAR(50)")
        )
        conn.commit()
    
    conn.close()
    print("Coluna task_id adicionada com sucesso!")
```

### 3.2 Otimização de Consultas

#### Exemplo para Remessas:

```python
@remessas.route('', methods=['GET'])
def listar_remessas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filtros
    status = request.args.get('status')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Query base
    query = Remessa.query
    
    # Aplicar filtros
    if status:
        query = query.filter(Remessa.status == status)
    if data_inicio:
        query = query.filter(Remessa.data_envio >= data_inicio)
    if data_fim:
        query = query.filter(Remessa.data_envio <= data_fim)
    
    # Ordenação e paginação
    query = query.order_by(Remessa.data_envio.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Preparar resposta
    remessas = pagination.items
    total = pagination.total
    
    return jsonify({
        'items': [remessa.to_dict() for remessa in remessas],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
```

#### Exemplo para Títulos:

```python
@titulos.route('', methods=['GET'])
def listar_titulos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filtros
    status = request.args.get('status')
    numero = request.args.get('numero')
    protocolo = request.args.get('protocolo')
    
    # Query base com joins otimizados
    query = Titulo.query.options(
        joinedload(Titulo.credor),
        joinedload(Titulo.devedor),
        joinedload(Titulo.remessa)
    )
    
    # Aplicar filtros
    if status:
        query = query.filter(Titulo.status == status)
    if numero:
        query = query.filter(Titulo.numero.ilike(f'%{numero}%'))
    if protocolo:
        query = query.filter(Titulo.protocolo.ilike(f'%{protocolo}%'))
    
    # Ordenação e paginação
    query = query.order_by(Titulo.data_cadastro.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Preparar resposta
    titulos = pagination.items
    total = pagination.total
    
    return jsonify({
        'items': [titulo.to_dict() for titulo in titulos],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
```

### 3.3 Implementação de Cache

```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# Inicializar cache
cache.init_app(app)

# Exemplo de endpoint com cache
@relatorios.route('/dashboard', methods=['GET'])
@cache.cached(timeout=300)  # Cache por 5 minutos
def dashboard():
    try:
        # Estatísticas de remessas
        total_remessas = Remessa.query.count()
        remessas_processadas = Remessa.query.filter_by(status='PROCESSADA').count()
        remessas_pendentes = Remessa.query.filter_by(status='EM_PROCESSAMENTO').count()
        remessas_erro = Remessa.query.filter_by(status='ERRO').count()
        
        # Estatísticas de títulos
        total_titulos = Titulo.query.count()
        titulos_protestados = Titulo.query.filter_by(status='PROTESTADO').count()
        titulos_em_cartorio = Titulo.query.filter_by(status='EM_CARTORIO').count()
        titulos_enviados = Titulo.query.filter_by(status='ENVIADO').count()
        
        # Estatísticas de desistências
        total_desistencias = Desistencia.query.count()
        desistencias_processadas = Desistencia.query.filter_by(status='PROCESSADA').count()
        desistencias_pendentes = Desistencia.query.filter_by(status='PENDENTE').count()
        
        # Estatísticas de erros
        total_erros = Erro.query.count()
        erros_resolvidos = Erro.query.filter_by(resolvido=True).count()
        erros_pendentes = Erro.query.filter_by(resolvido=False).count()
        
        return jsonify({
            'remessas': {
                'total': total_remessas,
                'processadas': remessas_processadas,
                'pendentes': remessas_pendentes,
                'erro': remessas_erro
            },
            'titulos': {
                'total': total_titulos,
                'protestados': titulos_protestados,
                'em_cartorio': titulos_em_cartorio,
                'enviados': titulos_enviados
            },
            'desistencias': {
                'total': total_desistencias,
                'processadas': desistencias_processadas,
                'pendentes': desistencias_pendentes
            },
            'erros': {
                'total': total_erros,
                'resolvidos': erros_resolvidos,
                'pendentes': erros_pendentes
            }
        })
    except Exception as e:
        app.logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
        return jsonify({'error': 'Erro ao obter dados do dashboard'}), 500
```

## 4. Inovações Propostas

### 4.1 Implementação de Cache Distribuído com Redis

```python
# Configuração do Redis
cache_config = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 300
}
app.config.from_mapping(cache_config)
cache.init_app(app)
```

### 4.2 Sistema de Monitoramento e Logging

```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Configuração de logging
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/protest_system.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Protest System startup')
```

## 5. Próximos Passos

1. Aplicar a correção do schema do banco
2. Implementar a configuração CORS robusta
3. Adaptar os endpoints para consultar o banco real
4. Implementar as otimizações de consulta
5. Testar todas as seções do frontend
6. Documentar as mudanças realizadas
