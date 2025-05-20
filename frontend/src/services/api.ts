// Serviço de API para o Sistema de Protesto
import axios from 'axios';

// API base URL com fallback para múltiplas portas
const getApiUrl = () => {
  // Prioridade 1: Variável de ambiente definida
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Prioridade 2: Tentar porta 5001 (porta do backend no docker-compose)
  return 'http://localhost:5001';
};

const API_URL = getApiUrl();
console.log('API URL configurada:', API_URL);

// Criar instância do axios com configurações base
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  // Aumentar timeout para evitar falhas em conexões lentas
  timeout: 10000,
  // Desabilitar credenciais para evitar problemas de CORS com preflight
  withCredentials: false
});

// Interceptor para adicionar o header de Basic Auth em todas as requisições
api.interceptors.request.use((config) => {
  const userCredentials = localStorage.getItem("userCredentials"); // Formato "username:password"
  if (userCredentials) {
    try {
      const base64Credentials = btoa(userCredentials); // btoa codifica para Base64
      config.headers.Authorization = `Basic ${base64Credentials}`;
    } catch (e) {
      console.error("Erro ao codificar credenciais para Base64:", e);
      // Lidar com o erro, talvez limpando as credenciais inválidas
      localStorage.removeItem("userCredentials");
    }
  }
  return config;
});

// Interceptor para tratamento global de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // O servidor respondeu com um status de erro
      console.error('Erro na resposta da API:', error.response.data);
      
      // Se for erro de não autorizado (401), redirecionar para o login
      // e limpar as credenciais armazenadas, pois podem estar inválidas ou expiradas
      if (error.response.status === 401) {
        localStorage.removeItem('userCredentials'); // Limpar credenciais Basic Auth
        // Adicionar um pequeno delay antes de redirecionar para garantir que o removeItem conclua
        // e para evitar loops de redirecionamento em alguns casos.
        setTimeout(() => {
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }, 100);
      }
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error('Sem resposta do servidor:', error.request);
    } else {
      // Erro ao configurar a requisição
      console.error('Erro na requisição:', error.message);
    }
    return Promise.reject(error);
  }
);

// Serviço para remessas
export const remessaService = {
  // Enviar uma nova remessa
  enviarRemessa: async (formData: FormData) => {
    try {
      // Alinhado com o backend: POST /api/remessas/upload
      const response = await api.post('/api/remessas/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao enviar remessa:", error);
      throw error;
    }
  },

  // Listar remessas
  listarRemessas: async (filtros?: any) => {
    try {
      const response = await api.get('/api/remessas', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao listar remessas:", error);
      throw error;
    }
  },

  // Obter detalhes de uma remessa
  obterRemessa: async (id: string) => {
    try {
      const response = await api.get(`/api/remessas/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao obter remessa ${id}:`, error);
      throw error;
    }
  }
};

// Serviço para desistências
export const desistenciaService = {
  // Enviar uma nova desistência
  enviarDesistencia: async (formData: FormData) => {
    try {
      // Garantir que o campo do arquivo seja nomeado como 'arquivo'
      // Se o formData contiver 'file', renomear para 'arquivo'
      if (formData.has('file') && !formData.has('arquivo')) {
        const file = formData.get('file');
        formData.delete('file');
        formData.append('arquivo', file as Blob);
      }
      
      // Atualizado para usar o endpoint correto
      const response = await api.post('/api/desistencias/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao enviar desistência:", error);
      throw error;
    }
  },

  // Listar desistências
  listarDesistencias: async (filtros?: any) => {
    try {
      // Atualizado para usar o endpoint correto
      const response = await api.get('/api/desistencias', {
        params: filtros
      });
      return response.data;
    } catch (error: any) {
      console.error("Erro ao listar desistências:", error);
      throw error;
    }
  }
};

// Serviço para títulos
export const titulosService = {
  // Listar títulos
  listarTitulos: async (filtros?: any) => {
    try {
      const response = await api.get('/api/titulos', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao listar títulos:", error);
      throw error;
    }
  },

  // Obter detalhes de um título
  obterTitulo: async (id: string) => {
    try {
      const response = await api.get(`/api/titulos/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao obter título ${id}:`, error);
      throw error;
    }
  }
};

// Serviço para erros
export const errosService = {
  // Listar erros
  listarErros: async (filtros?: any) => {
    try {
      const response = await api.get('/api/erros', {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao listar erros:", error);
      throw error;
    }
  },

  // Obter detalhes de um erro
  obterErro: async (id: string) => {
    try {
      const response = await api.get(`/api/erros/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao obter erro ${id}:`, error);
      throw error;
    }
  }
};

export default {
  api,
  remessaService,
  desistenciaService,
  titulosService,
  errosService
};
