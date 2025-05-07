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

// Configuração do axios
const api = axios.create({
  baseURL: '/api',
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
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

  // Função para verificar a sessão do usuário
  const checkSession = async (): Promise<boolean> => {
    const userDataStr = localStorage.getItem("userData");
    
    if (!userDataStr) {
      setUser(null);
      return false;
    }
    
    try {
      const userData = JSON.parse(userDataStr);
      setUser(userData);
      return true;
    } catch (error) {
      console.error("Erro ao verificar sessão:", error);
      logout();
      return false;
    }
  };

  // Função de login
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      console.log("Tentando fazer login com:", { email });
      
      const response = await api.post('/auth/login', {
        email,
        senha: password
      });
      
      console.log("Status da resposta:", response.status);
      
      if (response.status !== 200) {
        throw new Error(`Erro ${response.status}: ${response.data.error || 'Erro desconhecido'}`);
      }
      
      const { user: userData, access_token } = response.data;
      
      if (!userData) {
        throw new Error("Dados do usuário não retornados");
      }
      
      // Salvar o token e os dados do usuário
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("userData", JSON.stringify(userData));
      
      // Configurar o token no axios para futuras requisições
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Atualizar o estado do usuário
      setUser(userData);
    } catch (error) {
      console.error("Erro detalhado ao fazer login:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Função de logout
  const logout = () => {
    localStorage.removeItem("userData");
    localStorage.removeItem("access_token");
    delete api.defaults.headers.common['Authorization'];
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
