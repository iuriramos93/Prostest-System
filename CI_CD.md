# Pipeline CI/CD do Protest-System

## Visão Geral

O pipeline CI/CD do Protest-System é composto por três workflows principais:

1. **Continuous Integration (CI)**
2. **Continuous Deployment (CD)**
3. **Monitoramento e Rollback**

## Workflows

### 1. Continuous Integration (CI)

**Gatilhos:**
- Push para branches `main` e `develop`
- Pull Requests para `main` e `develop`
- Agendado (todo domingo à meia-noite)

**Jobs:**
- **Frontend:**
  - Instalação de dependências
  - Lint
  - Type check
  - Testes
  - Build
  - Cache de build

- **Backend:**
  - Instalação de dependências
  - Lint
  - Type check
  - Testes
  - Cobertura de código

- **SonarQube:**
  - Análise estática
  - Métricas de qualidade
  - Relatórios de cobertura

- **Notificações:**
  - Slack

### 2. Continuous Deployment (CD)

**Gatilhos:**
- Push para branches `main` e `develop`
- Conclusão bem-sucedida do workflow CI

**Jobs:**
- **Build e Push:**
  - Build de imagens Docker
  - Push para Docker Hub
  - Versionamento semântico
  - Cache de layers

- **Deploy Development:**
  - Deploy para ambiente de desenvolvimento
  - Health checks
  - Limpeza de recursos

- **Deploy Production:**
  - Deploy para ambiente de produção
  - Health checks
  - Limpeza de recursos

- **Health Check:**
  - Verificação de endpoints
  - Verificação de serviços
  - Verificação de banco de dados

- **Notificações:**
  - Slack

### 3. Monitoramento e Rollback

**Gatilhos:**
- Agendado (a cada 5 minutos)
- Manual (workflow_dispatch)

**Jobs:**
- **Monitoramento:**
  - Métricas do frontend
  - Métricas do backend
  - Conexão com banco de dados
  - Espaço em disco
  - Uso de memória
  - Saúde dos containers

- **Rollback:**
  - Rollback para versão anterior
  - Verificação de rollback
  - Limpeza de recursos

- **Notificações:**
  - Slack

## Configuração

### Secrets Necessários

```yaml
# Docker Hub
DOCKER_HUB_USERNAME: "seu-usuario"
DOCKER_HUB_ACCESS_TOKEN: "seu-token"

# Development
DEV_HOST: "dev.example.com"
DEV_USERNAME: "dev-user"
DEV_SSH_KEY: "chave-ssh"
DEV_FRONTEND_URL: "http://dev-frontend.example.com"
DEV_BACKEND_URL: "http://dev-backend.example.com"

# Production
PROD_HOST: "prod.example.com"
PROD_USERNAME: "prod-user"
PROD_SSH_KEY: "chave-ssh"
PROD_FRONTEND_URL: "http://prod-frontend.example.com"
PROD_BACKEND_URL: "http://prod-backend.example.com"

# Notifications
SLACK_WEBHOOK_URL: "webhook-url"

# Code Quality
SONAR_TOKEN: "sonar-token"
CODECOV_TOKEN: "codecov-token"
```

### Variáveis de Ambiente

```yaml
# Development
NODE_ENV: "development"
FLASK_ENV: "development"
DATABASE_URL: "postgresql://user:pass@db:5432/protest_dev"

# Production
NODE_ENV: "production"
FLASK_ENV: "production"
DATABASE_URL: "postgresql://user:pass@db:5432/protest_prod"
```

## Melhores Práticas

1. **Segurança:**
   - Use secrets para credenciais
   - Implemente rate limiting
   - Monitore vulnerabilidades
   - Faça scan de imagens Docker

2. **Performance:**
   - Use cache de dependências
   - Implemente build paralelo
   - Otimize imagens Docker
   - Monitore recursos

3. **Confiability:**
   - Implemente retry em falhas
   - Monitore health checks
   - Faça backup de dados
   - Implemente rollback automático

4. **Manutenção:**
   - Documente mudanças
   - Mantenha logs
   - Atualize dependências
   - Faça code review

## Troubleshooting

### Problemas Comuns

1. **Build Falha:**
   - Verifique logs
   - Verifique dependências
   - Verifique cache
   - Verifique recursos

2. **Deploy Falha:**
   - Verifique conexão SSH
   - Verifique permissões
   - Verifique recursos
   - Verifique logs

3. **Monitoramento Falha:**
   - Verifique endpoints
   - Verifique serviços
   - Verifique recursos
   - Verifique logs

### Logs

- GitHub Actions: `.github/workflows/*.yml`
- Docker: `docker logs`
- Application: `logs/`
- SonarQube: `sonar-project.properties`

## Links Úteis

- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker](https://docs.docker.com/)
- [SonarQube](https://docs.sonarqube.org/)
- [Codecov](https://docs.codecov.io/)
- [Slack API](https://api.slack.com/) 