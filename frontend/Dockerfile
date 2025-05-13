# Stage 1: Build the React application (Development & Production)
FROM node:18-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./

FROM base AS dependencies
RUN npm ci

FROM dependencies AS builder
COPY . .
RUN npm run build

# Stage 2: Serve the static files with Nginx (Production)
FROM nginx:stable-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf # Opcional: se tiver config Nginx customizada
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Stage for development (uses Vite dev server)
FROM dependencies AS development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
