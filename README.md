# Sistema de Protesto - Migração do Backend

Este documento descreve o processo de migração do backend Node.js para o backend Flask do Sistema de Protesto.

## Estrutura do Projeto

O projeto está estruturado da seguinte forma:

- **backend/**: Contém o código do backend Flask
  - **app/**: Contém os módulos da aplicação Flask
    - **auth/**: Módulo de autenticação
    - **remessas/**: Módulo de remessas
    - **desistencias/**: Módulo de desistências
    - **titulos/**: Módulo de títulos
    - **utils/**: Utilidades diversas
  - **config/**: Arquivos de configuração
  - **migrations/**: Migrações do banco de dados
  - **scripts/**: Scripts utilitários

- **src/**: Contém o código do frontend React
  - **backend/**: Contém o código do backend Node.js (a ser migrado)

## Migração do Backend Node.js para Flask

### Passo 1: Preparar o Ambiente

1. Certifique-se de ter o Docker e o Docker Compose instalados.
2. Crie um ambiente virtual Python para desenvolvimento local:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Passo 2: Executar Migrações do Banco de Dados

1. Crie a migração para adicionar o campo `descricao` ao modelo `Remessa`:

```bash
cd backend
python scripts/create_migration.py
```

2. Aplique a migração:

```bash
cd backend
python scripts/apply_migration.py
```

### Passo 3: Migrar Dados do Node.js para o Flask

1. Certifique-se de que o banco de dados PostgreSQL está em execução.
2. Execute o script de migração de dados:

```bash
cd backend
python scripts/migrate_js_to_flask.py
```

### Passo 4: Iniciar os Serviços com Docker Compose

1. Inicie os serviços usando Docker Compose:

```bash
docker-compose up -d
```

2. Verifique se os serviços estão em execução:

```bash
docker-compose ps
```

### Passo 5: Verificar a Migração

1. Acesse a API Flask em `http://localhost:5000/api/health` para verificar se está funcionando.
2. Acesse o frontend em `http://localhost:3002` para verificar se está se comunicando corretamente com a API Flask.

## Arquivos Migrados

Os seguintes arquivos do backend Node.js foram migrados para o backend Flask:

- **src/backend/routes/remessas.js** → **backend/app/remessas/routes.py**
- **src/backend/server.js** → **backend/app.py** e **backend/wsgi.py**

## Notas Adicionais

- O backend Flask usa SQLAlchemy como ORM, enquanto o backend Node.js usava consultas SQL diretas.
- A autenticação no backend Flask é feita usando JWT, assim como no backend Node.js.
- As rotas da API Flask seguem o mesmo padrão das rotas da API Node.js, facilitando a integração com o frontend existente.

## Troubleshooting

Se encontrar problemas durante a migração, verifique:

1. Logs dos containers Docker:

```bash
docker-compose logs api
```

2. Verifique se o banco de dados está acessível:

```bash
docker-compose exec api python -c "from app import db; db.session.execute('SELECT 1')"
```

3. Verifique se as migrações foram aplicadas corretamente:

```bash
docker-compose exec api flask db current
```