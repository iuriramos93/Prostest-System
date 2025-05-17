import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    hmr: {
      // Configuração para facilitar o desenvolvimento com HMR
      clientPort: 5173,
    },
    proxy: {
      '/api': {
        target: 'http://api:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-toast',
      'lucide-react',
      'recharts',
      'lodash',
      'class-variance-authority',
      'clsx'
    ],
    esbuildOptions: {
      // Necessário para resolver corretamente as importações de módulos ESM
      target: 'es2020',
    },
  },
  build: {
    target: 'es2020',
  },
}); 