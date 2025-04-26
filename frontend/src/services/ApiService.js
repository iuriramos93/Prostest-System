import axios from 'axios';
import { getAuthToken } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api`,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Interceptor para adicionar o token de autenticação em todas as requisições
    this.api.interceptors.request.use(
      (config) => {
        const token = getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para tratar erros de resposta
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Verifica se o erro é de CORS
        if (error.message === 'Network Error') {
          console.error('Erro de CORS ou conexão:', error);
        }
        
        // Verifica se o erro é de autenticação (401)
        if (error.response && error.response.status === 401) {
          console.error('Erro de autenticação:', error);
          // Aqui poderia redirecionar para a página de login
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * Lista todas as rotas disponíveis na API
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async listarEndpoints() {
    try {
      const response = await this.api.get('/routes');
      return response.data;
    } catch (error) {
      console.error('Erro ao listar endpoints:', error);
      throw error;
    }
  }

  /**
   * Verifica o status da API
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async verificarStatus() {
    try {
      const response = await this.api.get('/status');
      return response.data;
    } catch (error) {
      console.error('Erro ao verificar status da API:', error);
      throw error;
    }
  }

  /**
   * Método genérico para fazer requisições GET
   * @param {string} endpoint - Endpoint da API
   * @param {Object} params - Parâmetros da requisição
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async get(endpoint, params = {}) {
    try {
      const response = await this.api.get(endpoint, { params });
      return response.data;
    } catch (error) {
      console.error(`Erro ao fazer requisição GET para ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Método genérico para fazer requisições POST
   * @param {string} endpoint - Endpoint da API
   * @param {Object} data - Dados da requisição
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async post(endpoint, data = {}) {
    try {
      const response = await this.api.post(endpoint, data);
      return response.data;
    } catch (error) {
      console.error(`Erro ao fazer requisição POST para ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Método genérico para fazer requisições PUT
   * @param {string} endpoint - Endpoint da API
   * @param {Object} data - Dados da requisição
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async put(endpoint, data = {}) {
    try {
      const response = await this.api.put(endpoint, data);
      return response.data;
    } catch (error) {
      console.error(`Erro ao fazer requisição PUT para ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Método genérico para fazer requisições DELETE
   * @param {string} endpoint - Endpoint da API
   * @param {Object} params - Parâmetros da requisição
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async delete(endpoint, params = {}) {
    try {
      const response = await this.api.delete(endpoint, { params });
      return response.data;
    } catch (error) {
      console.error(`Erro ao fazer requisição DELETE para ${endpoint}:`, error);
      throw error;
    }
  }
}

export default new ApiService();