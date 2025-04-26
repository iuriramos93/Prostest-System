import axios from 'axios';
import { setAuthToken, removeAuthToken, getAuthToken } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class AuthService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/auth`,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Realiza o login do usuário
   * @param {string} email - Email do usuário
   * @param {string} senha - Senha do usuário
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async login(email, senha) {
    try {
      const response = await this.api.post('/login', { email, senha });
      
      if (response.data && response.data.token) {
        // Armazena o token no localStorage
        setAuthToken(response.data.token);
        
        // Retorna os dados do usuário
        return response.data;
      }
      
      throw new Error('Token não encontrado na resposta');
    } catch (error) {
      console.error('Erro ao realizar login:', error);
      throw error;
    }
  }

  /**
   * Realiza o logout do usuário
   */
  logout() {
    try {
      // Remove o token do localStorage
      removeAuthToken();
      
      // Opcional: notificar o backend sobre o logout
      return this.api.post('/logout', {}, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`
        }
      });
    } catch (error) {
      console.error('Erro ao realizar logout:', error);
      // Mesmo com erro, remove o token local
      removeAuthToken();
    }
  }

  /**
   * Verifica se o usuário está autenticado
   * @returns {boolean} - True se o usuário estiver autenticado
   */
  isAuthenticated() {
    const token = getAuthToken();
    return !!token; // Converte para booleano
  }

  /**
   * Obtém informações do usuário atual
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async getUserInfo() {
    try {
      const response = await this.api.get('/me', {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter informações do usuário:', error);
      throw error;
    }
  }
}

export default new AuthService();