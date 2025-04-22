
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios from "axios";

// Interface para o usuário
interface User {
  id: string;
  name?: string;
  nome_completo?: string;
  email: string;
  username?: string;
  cargo?: string;
  admin?: boolean;
}

// Interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkSession: () => Promise<boolean>;
}

// Criando o contexto de autenticação
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Configuração do axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para adicionar o token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Provider para o contexto de autenticação
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verificar se o usuário está autenticado ao carregar a página
  useEffect(() => {
    const checkAuth = async () => {
      await checkSession();
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Função para verificar a sessão do usuário
  const checkSession = async (): Promise<boolean> => {
    const token = localStorage.getItem("token");
    
    if (!token) {
      setUser(null);
      return false;
    }
    
    try {
      // Verificar se o token é válido fazendo uma requisição para obter os dados do usuário
      const response = await api.get("/auth/me");
      setUser(response.data);
      return true;
    } catch (error) {
      console.error("Erro ao verificar sessão:", error);
      // Se o token expirou ou é inválido, fazer logout
      logout();
      return false;
    }
  };

  // Função de login
  // Update the API URL to ensure it's correctly pointing to your API service
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  
  // Then update the login function to use the correct endpoint
  const login = async (email: string, password: string) => {
    try {
      // Note the URL format - make sure it matches your backend route structure
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      });
      
      const { access_token, user: userData } = response.data;
      
      // Salvar o token e os dados do usuário
      localStorage.setItem("token", access_token);
      
      // Atualizar o estado do usuário
      setUser(userData);
      setIsLoading(false);
    } catch (error) {
      setIsLoading(false);
      console.error("Erro ao fazer login:", error);
      throw error;
    }
  };

  // Função de logout
  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      checkSession
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook para utilizar o contexto de autenticação
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  
  return context;
}
