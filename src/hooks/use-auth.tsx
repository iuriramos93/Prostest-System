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

// API base URL - Usar o proxy configurado no Vite
const API_URL = '/api'; // Será redirecionado para http://localhost:5000 pelo proxy do Vite

// Configuração do axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Para enviar cookies CORS
});

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

  // Função para verificar a sessão do usuário (simplificada sem JWT)
  const checkSession = async (): Promise<boolean> => {
    const userDataStr = localStorage.getItem("userData");
    
    if (!userDataStr) {
      setUser(null);
      return false;
    }
    
    try {
      // Recuperar os dados do usuário do localStorage
      const userData = JSON.parse(userDataStr);
      setUser(userData);
      return true;
    } catch (error) {
      console.error("Erro ao verificar sessão:", error);
      logout();
      return false;
    }
  };

  // Função de login simplificada sem JWT
  const login = async (email: string, password: string) => {
    try {
      // Usando a URL base correta com o proxy configurado
      const response = await api.post(`/auth/login`, {
        email,
        password
      });
      
      // Extrair apenas os dados do usuário
      const { user: userData } = response.data;
      
      // Salvar os dados do usuário no localStorage para persistência
      localStorage.setItem("userData", JSON.stringify(userData));
      
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
    localStorage.removeItem("userData");
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
