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
    port: 3002,
    strictPort: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    }
  },
  build: {
    outDir: 'dist',
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
            '@radix-ui/react-tabs'
          ]
        },
        // Limita o tamanho dos chunks
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // Gera sourcemaps apenas em desenvolvimento
    sourcemap: true
  }
}) 