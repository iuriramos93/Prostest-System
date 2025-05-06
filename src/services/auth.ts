import { api } from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: number;
  nome_completo: string;
  email: string;
  cargo: string;
  admin: boolean;
  ativo: boolean;
  data_criacao: string;
}

class AuthService {
  async login(credentials: LoginCredentials) {
    try {
      const response = await api.post('/api/auth/login', credentials);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      return response.data;
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      throw error;
    }
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get('/api/auth/me');
      return response.data;
    } catch (error) {
      console.error('Erro ao obter usuário atual:', error);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}

export const authService = new AuthService(); 