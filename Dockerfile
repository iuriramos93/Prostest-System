# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build # Assuming there is a build script

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist # Assuming build output is in 'dist'
COPY --from=builder /app/node_modules ./node_modules # Or copy only production dependencies
COPY --from=builder /app/package.json ./

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"] # Assuming there is a start script for production
