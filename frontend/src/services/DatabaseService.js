import axios from 'axios';
import { getAuthToken } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class DatabaseService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/database`,
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
  }

  /**
   * Verifica o status da conexão com o banco de dados
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async verificarConexao() {
    try {
      const response = await this.api.get('/status');
      return response.data;
    } catch (error) {
      console.error('Erro ao verificar conexão com o banco de dados:', error);
      throw error;
    }
  }

  /**
   * Obtém informações sobre o volume de dados do PostgreSQL
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async obterInfoVolume() {
    try {
      const response = await this.api.get('/volume-info');
      return response.data;
    } catch (error) {
      console.error('Erro ao obter informações do volume:', error);
      throw error;
    }
  }

  /**
   * Executa backup do banco de dados
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async executarBackup() {
    try {
      const response = await this.api.post('/backup');
      return response.data;
    } catch (error) {
      console.error('Erro ao executar backup:', error);
      throw error;
    }
  }

  /**
   * Restaura backup do banco de dados
   * @param {string} backupId - ID do backup a ser restaurado
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async restaurarBackup(backupId) {
    try {
      const response = await this.api.post(`/restore/${backupId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao restaurar backup:', error);
      throw error;
    }
  }

  /**
   * Lista backups disponíveis
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async listarBackups() {
    try {
      const response = await this.api.get('/backups');
      return response.data;
    } catch (error) {
      console.error('Erro ao listar backups:', error);
      throw error;
    }
  }
}

export default new DatabaseService();