# Dockerfile para ambiente de desenvolvimento do frontend (React/Vite)
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

RUN npm run build

# Instala o servidor web estático (serve)
RUN npm install -g serve

# Comando para servir os arquivos estáticos do build na porta 80
CMD ["serve", "-s", "dist", "-l", "80"]

EXPOSE 80


