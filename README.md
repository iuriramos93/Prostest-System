# Prostest-System

Sistema de Gerenciamento de Protestos de Títulos para Cartórios

## Visão Geral

O Prostest-System é uma aplicação web completa para gerenciamento de protestos de títulos em cartórios, permitindo o envio de remessas, controle de desistências, geração de relatórios e muito mais. O sistema é composto por um frontend React com TypeScript e um backend Flask com PostgreSQL.

## Estrutura do Projeto

```
Prostest-System/
├── frontend/               # Frontend React/TypeScript
│   ├── src/                # Código fonte do frontend
│   ├── public/             # Arquivos estáticos
│   ├── Dockerfile          # Configuração Docker para o frontend
│   └── package.json        # Dependências do frontend
├── backend/                # Backend Flask
│   ├── app/                # Código fonte do backend
│   │   ├── __init__.py     # Inicialização da aplicação Flask
│   │   ├── auth/           # Módulo de autenticação
│   │   ├── remessas/       # Módulo de remessas
│   │   ├── relatorios/     # Módulo de relatórios
│   │   └── utils/          # Utilitários
│   ├── Dockerfile          # Configuração Docker para o backend
│   └── requirements.txt    # Dependências do backend
├── sql_scripts/            # Scripts SQL para inicialização do banco
│   ├── database_schema.sql # Esquema do banco de dados
│   └── dados_teste.sql     # Dados de teste
├── docker-compose.yml      # Configuração Docker Compose para desenvolvimento
├── .env.example            # Exemplo de variáveis de ambiente
└── .env.prod.example       # Exemplo de variáveis de ambiente para produção
```

## Funcionalidades Principais

- **Autenticação**: Sistema de autenticação Basic Auth seguro
- **Remessas**: Envio e processamento de remessas de títulos
- **Desistências**: Gerenciamento de desistências de protesto
- **Relatórios**: Geração de relatórios e estatísticas
- **Exportação**: Exportação de dados em CSV, PDF e Excel
- **Dashboard**: Visualização de métricas e indicadores

## Requisitos

- Docker e Docker Compose
- Node.js 16+ (apenas para desenvolvimento local do frontend)
- Python 3.9+ (apenas para desenvolvimento local do backend)
- PostgreSQL 13+ (gerenciado pelo Docker em desenvolvimento)

## Instalação e Execução

### Usando Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Prostest-System.git
   cd Prostest-System
   ```

2. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env conforme necessário
   ```

3. Inicie os contêineres:
   ```bash
   docker-compose up -d
   ```

4. Acesse a aplicação:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - pgAdmin: http://localhost:5050 (credenciais no .env)

### Desenvolvimento Local

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py
```

## Endpoints da API

### Autenticação

- `POST /api/auth/login`: Autenticação de usuário
- `GET /api/auth/logout`: Logout de usuário
- `GET /api/auth/me`: Informações do usuário autenticado

### Remessas

- `GET /api/remessas`: Lista remessas com paginação e filtros
  - Parâmetros: `tipo`, `uf`, `status`, `dataInicio`, `dataFim`, `page`, `per_page`
- `GET /api/remessas/<id>`: Detalhes de uma remessa específica
- `POST /api/remessas/upload`: Envio de nova remessa
- `GET /api/remessas/estatisticas`: Estatísticas de remessas
- `GET /api/remessas/exportar`: Exportação de remessas para CSV

### Desistências

- `GET /api/remessas?tipo=Desistência`: Lista desistências com paginação e filtros
- `POST /api/remessas/desistencias`: Envio de nova desistência

### Relatórios

- `GET /api/relatorios/dashboard`: Dados para o dashboard
- `GET /api/relatorios/titulos`: Relatório de títulos
- `GET /api/relatorios/desistencias`: Relatório de desistências

## Paginação

As rotas que retornam listas de objetos suportam paginação através dos seguintes parâmetros:

- `page`: Número da página (começa em 1)
- `per_page`: Itens por página (padrão: 10, máximo: 100)

Exemplo de resposta paginada:

```json
{
  "items": [...],
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 42,
    "pages": 5,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

## Exportação de Dados

O sistema suporta exportação de dados em diferentes formatos:

- **CSV**: Implementado e disponível para todas as listagens
- **Excel**: Em desenvolvimento
- **PDF**: Em desenvolvimento

Para exportar dados, use o botão "Exportar" disponível nas telas de listagem ou acesse diretamente os endpoints de exportação.

## Deploy em Produção

Para deploy em produção, siga estas etapas:

1. Configure as variáveis de ambiente para produção:
   ```bash
   cp .env.prod.example .env.prod
   # Edite o arquivo .env.prod com valores seguros para produção
   ```

2. Construa e inicie os contêineres de produção:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Configure um servidor web (Nginx, Apache) como proxy reverso para os serviços.

4. Configure certificados SSL para HTTPS.

## CI/CD com GitHub Actions

Para configurar CI/CD com GitHub Actions:

1. Crie um arquivo `.github/workflows/main.yml` com o seguinte conteúdo:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest

  build-and-deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker images
        run: |
          echo "Implementar build e push das imagens Docker"
      - name: Deploy to server
        run: |
          echo "Implementar deploy no servidor de produção"
```

2. Configure os secrets necessários no repositório GitHub.

## Manutenção e Backup

### Backup do Banco de Dados

```bash
# Backup
docker exec protestsystem-db pg_dump -U postgres protest_system > backup_$(date +%Y%m%d).sql

# Restauração
cat backup_20250517.sql | docker exec -i protestsystem-db psql -U postgres protest_system
```

### Logs

```bash
# Visualizar logs do backend
docker-compose logs -f api

# Visualizar logs do frontend
docker-compose logs -f frontend

# Visualizar logs do banco de dados
docker-compose logs -f db
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Contato

Para suporte ou dúvidas, entre em contato com a equipe de desenvolvimento.
