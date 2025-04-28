# Instruções de Deploy do Sistema de Protesto

Este documento fornece instruções detalhadas para implantação do Sistema de Protesto em ambiente de produção.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Ambiente](#configuração-do-ambiente)
3. [Deploy com Docker](#deploy-com-docker)
4. [Deploy Manual](#deploy-manual)
5. [Configuração de Banco de Dados](#configuração-de-banco-de-dados)
6. [Configuração de Proxy Reverso](#configuração-de-proxy-reverso)
7. [Monitoramento e Logging](#monitoramento-e-logging)
8. [Backup Automatizado](#backup-automatizado)
9. [Migração de Dados](#migração-de-dados)

## Pré-requisitos

- Servidor Linux (Ubuntu 20.04 LTS ou superior recomendado)
- Docker e Docker Compose
- Nginx (para proxy reverso)
- PostgreSQL 13+ (se não estiver usando Docker)
- Certificado SSL (Let's Encrypt recomendado)

## Configuração do Ambiente

### Variáveis de Ambiente

1. Clone o repositório:
   ```bash
   git clone https://github.com/buziodev/ProtestSystem.git
   cd ProtestSystem
   ```

2. Configure as variáveis de ambiente:
   ```bash
   cd backend
   cp .env.example .env
   ```

3. Edite o arquivo `.env` com as configurações de produção:
   ```
   FLASK_ENV=production
   SECRET_KEY=sua_chave_secreta_muito_segura
   JWT_SECRET_KEY=outra_chave_secreta_muito_segura
   DATABASE_URL=postgresql://usuario:senha@db:5432/protest_db
   REDIS_URL=redis://redis:6379/0
   ```

## Deploy com Docker

### Usando Docker Compose

1. Ajuste o arquivo `docker-compose.yml` para ambiente de produção:
   ```bash
   cp docker-compose.yml docker-compose.prod.yml
   ```

2. Edite `docker-compose.prod.yml` para configurações de produção:
   - Remova volumes de desenvolvimento
   - Configure restart policies para `always`
   - Ajuste portas conforme necessário

3. Inicie os serviços:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. Inicialize o banco de dados (primeira execução):
   ```bash
   docker-compose -f docker-compose.prod.yml exec api flask db upgrade
   docker-compose -f docker-compose.prod.yml exec api flask seed-db  # Se disponível
   ```

## Deploy Manual

### Backend (Flask)

1. Configure um ambiente virtual Python:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure o Gunicorn como servidor WSGI:
   ```bash
   pip install gunicorn
   ```

3. Crie um script de serviço systemd `/etc/systemd/system/protest-api.service`:
   ```
   [Unit]
   Description=Protest System API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/ProtestSystem/backend
   Environment="PATH=/path/to/ProtestSystem/backend/venv/bin"
   ExecStart=/path/to/ProtestSystem/backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. Ative e inicie o serviço:
   ```bash
   sudo systemctl enable protest-api
   sudo systemctl start protest-api
   ```

### Frontend (React)

1. Construa o frontend para produção:
   ```bash
   cd /path/to/ProtestSystem
   npm install
   npm run build
   ```

2. Configure o Nginx para servir os arquivos estáticos:
   ```
   server {
       listen 80;
       server_name seu-dominio.com;

       location / {
           root /path/to/ProtestSystem/dist;
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Configuração de Banco de Dados

### PostgreSQL

1. Instale o PostgreSQL (se não estiver usando Docker):
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. Configure o banco de dados:
   ```bash
   sudo -u postgres psql
   ```

3. No prompt do PostgreSQL:
   ```sql
   CREATE DATABASE protest_db;
   CREATE USER protest_user WITH ENCRYPTED PASSWORD 'senha_segura';
   GRANT ALL PRIVILEGES ON DATABASE protest_db TO protest_user;
   \q
   ```

4. Importe o esquema inicial:
   ```bash
   psql -U protest_user -d protest_db -f /path/to/ProtestSystem/database_schema.sql
   ```

## Configuração de Proxy Reverso

### Nginx com SSL

1. Instale o Nginx e Certbot:
   ```bash
   sudo apt update
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. Obtenha um certificado SSL:
   ```bash
   sudo certbot --nginx -d seu-dominio.com
   ```

3. Configure o Nginx para HTTPS:
   ```
   server {
       listen 443 ssl;
       server_name seu-dominio.com;

       ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

       # Configurações de segurança SSL
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_prefer_server_ciphers on;
       ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
       ssl_session_cache shared:SSL:10m;
       ssl_session_timeout 10m;

       # Headers de segurança
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
       add_header X-Content-Type-Options nosniff;
       add_header X-Frame-Options DENY;
       add_header X-XSS-Protection "1; mode=block";

       location / {
           root /path/to/ProtestSystem/dist;
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

   server {
       listen 80;
       server_name seu-dominio.com;
       return 301 https://$host$request_uri;
   }
   ```

## Monitoramento e Logging

### Configuração de Logs

1. Configure logs do aplicativo no arquivo `.env`:
   ```
   LOG_LEVEL=INFO
   LOG_FILE=/var/log/protest-system/app.log
   ```

2. Configure rotação de logs com logrotate:
   ```
   /var/log/protest-system/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
   }
   ```

### Monitoramento com Prometheus e Grafana

1. Adicione o exportador Prometheus ao backend:
   ```bash
   pip install prometheus-flask-exporter
   ```

2. Configure o Prometheus para coletar métricas:
   ```yaml
   # /etc/prometheus/prometheus.yml
   scrape_configs:
     - job_name: 'protest-system'
       scrape_interval: 15s
       static_configs:
         - targets: ['localhost:5000']
   ```

3. Configure dashboards no Grafana para visualizar métricas.

## Backup Automatizado

### Backup do Banco de Dados

1. Crie um script de backup `/usr/local/bin/backup-protest-db.sh`:
   ```bash
   #!/bin/bash
   BACKUP_DIR=/var/backups/protest-system
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   BACKUP_FILE=$BACKUP_DIR/protest_db_$TIMESTAMP.sql.gz

   # Criar diretório de backup se não existir
   mkdir -p $BACKUP_DIR

   # Realizar backup
   pg_dump -U protest_user protest_db | gzip > $BACKUP_FILE

   # Manter apenas os últimos 30 backups
   ls -tp $BACKUP_DIR/*.sql.gz | grep -v '/$' | tail -n +31 | xargs -I {} rm -- {}
   ```

2. Torne o script executável:
   ```bash
   chmod +x /usr/local/bin/backup-protest-db.sh
   ```

3. Configure um cron job para executar diariamente:
   ```
   0 2 * * * /usr/local/bin/backup-protest-db.sh
   ```

### Backup de Arquivos

1. Configure rsync para backup de arquivos:
   ```bash
   rsync -avz --delete /path/to/ProtestSystem /path/to/backup/destination
   ```

2. Automatize com cron:
   ```
   0 3 * * * rsync -avz --delete /path/to/ProtestSystem /path/to/backup/destination
   ```

## Migração de Dados

### De Sistemas Legados

1. Exporte dados do sistema legado em formato CSV ou SQL.

2. Crie scripts de migração personalizados em `/path/to/ProtestSystem/backend/app/scripts/migracao/`.

3. Execute os scripts de migração:
   ```bash
   cd /path/to/ProtestSystem/backend
   source venv/bin/activate
   python -m app.scripts.migracao.importar_dados --arquivo=/path/to/dados_exportados.csv
   ```

4. Verifique a integridade dos dados após a migração:
   ```bash
   python -m app.scripts.migracao.verificar_integridade
   ```

### Atualização de Versão

1. Faça backup do banco de dados e arquivos antes da atualização.

2. Atualize o código-fonte:
   ```bash
   cd /path/to/ProtestSystem
   git pull
   ```

3. Atualize dependências:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Execute migrações de banco de dados:
   ```bash
   flask db upgrade
   ```

5. Reconstrua o frontend:
   ```bash
   cd /path/to/ProtestSystem
   npm install
   npm run build
   ```

6. Reinicie os serviços:cp docker-compose.yml docker-compose.prod.yml
   ```bash
   sudo systemctl restart protest-api
   sudo systemctl restart nginx
   ```

---

Em caso de problemas durante o deploy, consulte os logs do sistema:
- Logs do backend: `/var/log/protest-system/app.log`
- Logs do Nginx: `/var/log/nginx/error.log`
- Logs do sistema: `journalctl -u protest-api`