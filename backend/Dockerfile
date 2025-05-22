FROM python:3.9-slim

WORKDIR /app

# Adiciona explicitamente /app ao PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Variáveis de ambiente para configuração do Gunicorn (podem ser sobrescritas no docker-compose)
ENV GUNICORN_WORKERS 4
ENV GUNICORN_TIMEOUT 120

# Criar um usuário e grupo não-root
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin -c "Docker image user" appuser
RUN chown -R appuser:appuser /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretório para logs e mudar propriedade
RUN mkdir -p logs && chown -R appuser:appuser logs

# Mudar para o usuário não-root
USER appuser

# Expor a porta correta da API
EXPOSE 5001

# HEALTHCHECK para verificar se a aplicação está respondendo na porta 5001
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# Script de espera para o banco de dados
COPY --chown=appuser:appuser scripts/wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# Comando para esperar o banco de dados, criar o banco, rodar as migrations e depois iniciar o servidor
CMD ["sh", "-c", "/app/wait-for-db.sh db:5432 -- python /app/scripts/init_db.py && alembic upgrade head && gunicorn --bind 0.0.0.0:5001 --workers ${GUNICORN_WORKERS} --timeout ${GUNICORN_TIMEOUT} wsgi:app"]