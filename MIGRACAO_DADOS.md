# Migração de Dados do Backend Node.js para Flask

Este documento fornece instruções detalhadas sobre como migrar os dados do backend Node.js para o backend Flask do Sistema de Protesto.

## Visão Geral

O processo de migração envolve:

1. Extrair dados do banco de dados PostgreSQL usado pelo servidor Node.js
2. Transformar os dados para o formato esperado pelo servidor Flask
3. Carregar os dados no banco de dados usado pelo servidor Flask

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+ instalado
- Acesso ao banco de dados PostgreSQL usado pelo servidor Node.js

## Preparação do Ambiente

### 1. Configurar Ambiente Virtual Python

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verificar Conexão com o Banco de Dados

Edite o arquivo `backend/scripts/migrate_js_to_flask.py` e verifique se as configurações de conexão com o banco de dados estão corretas:

```python
# Configurações de conexão - ajuste conforme necessário
conn = psycopg2.connect(
    host="127.0.0.1",
    database="protest_system",
    user="protest_app",
    password="senha_segura",
    port=5432
)
```

## Processo de Migração

### 1. Criar Migração para o Campo Descrição

O modelo `Remessa` no servidor Flask precisa do campo `descricao` para compatibilidade com o modelo do servidor Node.js.

```bash
cd backend
python scripts/create_migration.py
```

### 2. Aplicar a Migração

```bash
cd backend
python scripts/apply_migration.py
```

### 3. Executar o Script de Migração de Dados

```bash
cd backend
python scripts/migrate_js_to_flask.py
```

Este script:
- Conecta-se ao banco de dados do Node.js
- Lê os dados das tabelas relevantes
- Mapeia os dados para os modelos do Flask
- Insere os dados no banco de dados do Flask

## Verificação da Migração

### 1. Verificar Contagem de Registros

Você pode verificar se a quantidade de registros foi migrada corretamente usando os seguintes comandos:

```bash
# No banco de dados do Node.js
psql -h 127.0.0.1 -U protest_app -d protest_system -c "SELECT COUNT(*) FROM remessas"
psql -h 127.0.0.1 -U protest_app -d protest_system -c "SELECT COUNT(*) FROM titulos"

# No banco de dados do Flask (após iniciar os containers)
docker-compose exec api python -c "from app import create_app, db; from app.models import Remessa, Titulo; app = create_app(); with app.app_context(): print(f'Remessas: {Remessa.query.count()}'); print(f'Titulos: {Titulo.query.count()}')"
```

### 2. Verificar Integridade dos Dados

Você pode verificar a integridade dos dados migrados acessando a API Flask:

```bash
# Verificar remessas
curl http://localhost:5001/api/remessas

# Verificar títulos
curl http://localhost:5001/api/titulos
```

## Resolução de Problemas

### Problema: Erro de Conexão com o Banco de Dados

Se você encontrar erros de conexão com o banco de dados, verifique:

1. Se o PostgreSQL está em execução
2. Se as credenciais de conexão estão corretas
3. Se o banco de dados existe

### Problema: Erro de Mapeamento de Dados

Se você encontrar erros relacionados ao mapeamento de dados, verifique:

1. A estrutura das tabelas no banco de dados do Node.js
2. Os modelos no servidor Flask
3. A lógica de mapeamento no script de migração

### Problema: Dados Duplicados

Se você encontrar dados duplicados após a migração:

1. Limpe o banco de dados do Flask antes de executar a migração novamente:

```bash
docker-compose exec api python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.drop_all(); db.create_all()"
```

2. Execute o script de migração novamente

## Considerações Finais

- A migração de dados é um processo delicado e pode exigir ajustes específicos dependendo da estrutura e quantidade de dados.
- Sempre faça backup dos dados antes de iniciar o processo de migração.
- Considere executar a migração em um ambiente de teste antes de aplicar em produção.

## Referências

- [Documentação do SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentação do Flask-Migrate](https://flask-migrate.readthedocs.io/)
- [Documentação do psycopg2](https://www.psycopg.org/docs/)