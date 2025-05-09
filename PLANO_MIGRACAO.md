# Plano de Migração do Backend Node.js para Flask

Este documento descreve o plano detalhado para migrar o backend do Sistema de Protesto da tecnologia Node.js para Flask.

## Visão Geral

O Sistema de Protesto atualmente possui um backend implementado em Node.js (Express) e um frontend em React. O objetivo é migrar o backend para Flask (Python) mantendo a compatibilidade com o frontend existente.

## Arquitetura Atual vs. Nova

### Arquitetura Atual
- **Backend**: Node.js com Express
- **Frontend**: React
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT

### Nova Arquitetura
- **Backend**: Python com Flask
- **Frontend**: React (mantido)
- **Banco de Dados**: PostgreSQL (mantido)
- **Autenticação**: JWT (mantido)

## Etapas da Migração

### 1. Preparação do Ambiente

1. **Configurar o ambiente de desenvolvimento Flask**:
   - Criar ambiente virtual Python
   - Instalar dependências necessárias
   - Configurar estrutura do projeto Flask

2. **Configurar Docker e Docker Compose**:
   - Atualizar Dockerfile para o backend Flask
   - Atualizar docker-compose.yml para incluir o novo backend

### 2. Migração de Modelos e Banco de Dados

1. **Mapear modelos do Node.js para SQLAlchemy**:
   - Identificar todos os modelos existentes
   - Criar modelos equivalentes em SQLAlchemy
   - Adicionar relacionamentos e validações

2. **Configurar migrações de banco de dados**:
   - Configurar Flask-Migrate
   - Criar migrações iniciais
   - Adicionar campo `descricao` ao modelo `Remessa`

3. **Migrar dados existentes**:
   - Criar script para extrair dados do banco Node.js
   - Transformar dados para o formato do Flask
   - Inserir dados no banco do Flask

### 3. Migração de Rotas e Controladores

1. **Mapear rotas da API Node.js**:
   - Listar todas as rotas existentes
   - Identificar parâmetros, métodos HTTP e respostas

2. **Implementar rotas equivalentes em Flask**:
   - Criar blueprints para cada módulo
   - Implementar controladores
   - Manter mesma estrutura de URL para compatibilidade

3. **Migrar lógica de negócios**:
   - Converter funções JavaScript para Python
   - Implementar validações e regras de negócio
   - Manter comportamento consistente

### 4. Migração de Autenticação e Autorização

1. **Configurar JWT no Flask**:
   - Instalar e configurar Flask-JWT-Extended
   - Implementar rotas de autenticação
   - Configurar middleware de autorização

2. **Migrar usuários e permissões**:
   - Migrar tabela de usuários
   - Configurar roles e permissões
   - Manter compatibilidade de tokens

### 5. Testes e Validação

1. **Implementar testes unitários e de integração**:
   - Testar modelos e validações
   - Testar rotas e controladores
   - Testar autenticação e autorização

2. **Validar compatibilidade com frontend**:
   - Testar integração com o frontend React
   - Verificar formatos de resposta
   - Ajustar conforme necessário

### 6. Implantação e Monitoramento

1. **Configurar ambiente de produção**:
   - Configurar Gunicorn como servidor WSGI
   - Configurar logs e monitoramento
   - Configurar variáveis de ambiente

2. **Estratégia de implantação**:
   - Implantar em ambiente de staging
   - Testar com dados reais
   - Migrar para produção com período de transição

## Arquivos Migrados

### Arquivos do Node.js a serem migrados:

1. **src/backend/server.js** → **backend/app.py** e **backend/wsgi.py**
   - Configuração do servidor Express → Configuração do Flask
   - Middlewares → Middlewares Flask
   - Rotas principais → Blueprints Flask

2. **src/backend/routes/remessas.js** → **backend/app/remessas/routes.py**
   - Rotas de remessas → Blueprint de remessas
   - Controladores → Funções de rota Flask
   - Validações → Esquemas de validação Flask

3. **src/backend/routes/desistencias.js** → **backend/app/desistencias/routes.py**
   - Rotas de desistências → Blueprint de desistências
   - Controladores → Funções de rota Flask

4. **src/backend/models/** → **backend/app/models.py**
   - Modelos Sequelize → Modelos SQLAlchemy
   - Validações → Validações SQLAlchemy

5. **src/backend/middleware/** → **backend/app/auth/middleware.py**
   - Middleware de autenticação → Decoradores Flask

## Cronograma

| Etapa | Duração Estimada | Dependências |
|-------|------------------|-------------|
| Preparação do Ambiente | 1 dia | - |
| Migração de Modelos e Banco de Dados | 3 dias | Preparação do Ambiente |
| Migração de Rotas e Controladores | 5 dias | Migração de Modelos |
| Migração de Autenticação | 2 dias | Migração de Modelos |
| Testes e Validação | 3 dias | Todas as etapas anteriores |
| Implantação | 1 dia | Testes e Validação |

## Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|--------------|-----------|
| Incompatibilidade com o frontend | Alto | Médio | Manter mesma estrutura de API, testes extensivos |
| Perda de dados na migração | Alto | Baixo | Backups, scripts de verificação, ambiente de teste |
| Performance inferior | Médio | Baixo | Otimização, caching, monitoramento |
| Bugs na lógica de negócio | Alto | Médio | Testes unitários e de integração, QA |

## Conclusão

A migração do backend Node.js para Flask permitirá uma melhor integração com o ecossistema Python, mantendo a compatibilidade com o frontend React existente. O plano detalhado acima fornece um roteiro para realizar essa migração de forma estruturada e com riscos minimizados. 