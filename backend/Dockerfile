FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p logs

# Expor a porta
EXPOSE 5000

# Script de inicialização
COPY scripts/init_db.py /app/scripts/
RUN chmod +x /app/scripts/init_db.py

# Comando para iniciar a aplicação
CMD ["sh", "-c", "python scripts/init_db.py && gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app"]