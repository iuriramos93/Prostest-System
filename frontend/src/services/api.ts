// Serviço de API para o Sistema de Protesto
import axios from 'axios';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// Criar instância do axios com configurações base
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
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
      // Alinhado com a sugestão do plano: POST /api/remessas/desistencias
      // Nota: Este endpoint pode precisar ser criado ou ajustado no backend.
      const response = await api.post('/api/remessas/desistencias', formData, {
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
      // Alinhado com a sugestão do plano: GET /api/remessas com filtro tipo=Desistência
      // Nota: O backend precisa suportar este filtro.
      const response = await api.get('/api/remessas', {
        params: { ...filtros, tipo: "Desistência" }
      });
      return response.data;
    } catch (error: any) {
      console.error("Erro ao listar desistências:", error);
      // A lógica de dados simulados foi removida para produção.
      // O erro será propagado para ser tratado pela interface do usuário.
      throw error;
    }
  }
};

export default {
  api,
  remessaService,
  desistenciaService
};
