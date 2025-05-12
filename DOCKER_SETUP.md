# Relatório de Ajustes Docker e GitHub Actions - Prostest-System

## Alterações Realizadas

### 1. Ajustes nos Arquivos Docker

#### 1.1 Docker Compose
- Alterado o volume do banco de dados para montar os scripts SQL automaticamente:
  - De: `./sql_scripts:/sql_scripts`
  - Para: `./sql_scripts:/docker-entrypoint-initdb.d`
  - Isso garante que os scripts `database_schema.sql` e `dados_teste.sql` sejam executados automaticamente na inicialização do banco de dados.

#### 1.2 Dockerfile do Backend
- Alterado o bind do Gunicorn para permitir acesso externo:
  - De: `127.0.0.1:5000` (apenas localhost)
  - Para: `0.0.0.0:5000` (todas as interfaces)
  - Isso garante que o serviço seja acessível de fora do container, essencial para comunicação entre containers.

### 2. Estrutura de Arquivos Docker
- Identificada a estrutura correta dos arquivos Docker:
  - `Dockerfile` na raiz do projeto (para o frontend)
  - `backend/Dockerfile` (para o backend Flask)
  - `docker-compose.yml` na raiz do projeto (configuração principal)
  - `backend/docker-compose.yml` (configuração secundária, não utilizada)

### 3. Configuração do GitHub Actions
- Criado arquivo de workflow em `.github/workflows/ci.yml` com:
  - Build da imagem Docker do backend
  - Build da imagem Docker do frontend
  - Estrutura comentada para adição de testes (backend, frontend e integração)
  - Configuração para execução em push e pull requests nas branches principais

## Instruções para Execução Local

Para executar o projeto em sua máquina local:

1. Certifique-se de ter Docker e Docker Compose instalados
2. Clone o repositório: `git clone https://github.com/buziodev/Prostest-System.git`
3. Navegue até a pasta do projeto: `cd Prostest-System`
4. Execute: `docker-compose up --build`
5. Acesse:
   - Frontend: http://localhost:3002
   - Backend API: http://localhost:5000
   - PGAdmin (gerenciamento do banco): http://localhost:5050
     - Email: admin@protestsystem.com
     - Senha: admin

## Observações Importantes

1. **Schema do Banco de Dados**: Os scripts SQL em `sql_scripts/` serão executados automaticamente na primeira inicialização do banco de dados. Se você já tiver um volume persistente, pode ser necessário removê-lo para que os scripts sejam executados novamente: `docker volume rm protestsystem_pgdata`

2. **Usuário Padrão**: O script `init_db.py` cria um usuário administrador padrão:
   - Email: admin@protestsystem.com
   - Senha: admin123

3. **GitHub Actions**: O workflow configurado fará o build das imagens Docker quando houver push ou pull request nas branches principais. Para configurar o push das imagens para um registry (Docker Hub, GitHub Container Registry, etc.), descomente e configure as linhas relevantes no arquivo `.github/workflows/ci.yml`.

## Próximos Passos Recomendados

1. Adicionar testes automatizados para o backend e frontend
2. Configurar etapas de deploy no workflow do GitHub Actions
3. Implementar verificação de segurança das imagens Docker
4. Considerar a utilização de variáveis de ambiente via GitHub Secrets para credenciais e configurações sensíveis
