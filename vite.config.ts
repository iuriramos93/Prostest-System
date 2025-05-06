import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { compression } from 'vite-plugin-compression2'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Adiciona compressão gzip para arquivos estáticos
    compression({
      algorithm: 'gzip',
      exclude: [/\.(br)$/, /\.(gz)$/],
      threshold: 1024, // Tamanho mínimo para compressão (1KB)
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // Configurações do servidor de desenvolvimento
    host: '0.0.0.0',
    port: 3002, // Mudando para 3002 porque a 3001 está ocupada
    strictPort: false, // Permitir que use a próxima porta se 3002 estiver ocupada
    cors: true, // Habilita CORS para todas as requisições do servidor de desenvolvimento
    hmr: {
      // Configuração do HMR
      host: 'localhost',
      protocol: 'ws',
      port: 3002, // Usa a mesma porta que o servidor Vite
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Enviando requisição para:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Recebendo resposta de:', req.method, req.url, proxyRes.statusCode);
          });
        },
      }
    }
  },
  build: {
    // Otimizações de build
    target: 'es2015',
    minify: 'terser',
    cssMinify: true,
    // Configuração de code splitting
    rollupOptions: {
      output: {
        // Separa vendor chunks para melhor cache
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: [
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-toast',
            '@radix-ui/react-tabs',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-label',
            '@radix-ui/react-progress',
            '@radix-ui/react-select',
            '@radix-ui/react-toggle',
            '@radix-ui/react-toggle-group',
            '@radix-ui/react-slot',
            '@radix-ui/react-scroll-area',
            '@radix-ui/react-separator'
          ],
        },
        // Limita o tamanho dos chunks
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // Gera sourcemaps apenas em desenvolvimento
    sourcemap: process.env.NODE_ENV !== 'production',
  },
}) 