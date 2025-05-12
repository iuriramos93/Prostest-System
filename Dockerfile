# Stage 1: Build the React application
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar arquivos de configuração e dependências primeiro para otimizar o cache
COPY package.json package-lock.json* ./

# Instalar dependências de forma limpa
RUN npm ci

# Copiar o restante do código fonte
COPY . .

# Construir a aplicação para produção
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:stable-alpine

# Copiar os arquivos estáticos construídos do estágio anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar uma configuração personalizada do Nginx (opcional, mas recomendado)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expor a porta 80 (padrão do Nginx)
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
