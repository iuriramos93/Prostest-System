import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api as axiosApiInstance } from "../services/api"; // Importa a instância configurada do api.ts

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
  login: (email: string, password: string) => Promise<User | null>; // Retorna o usuário ou null
  logout: () => void;
  checkSession: () => Promise<boolean>;
}

// Criando o contexto de autenticação
const AuthContext = createContext<AuthContextType | undefined>(undefined);

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

  // Função para verificar a sessão do usuário (baseado em credenciais e dados do usuário no localStorage)
  const checkSession = async (): Promise<boolean> => {
    setIsLoading(true);
    const userCredentials = localStorage.getItem("userCredentials");
    const userDataStr = localStorage.getItem("userData");

    if (userCredentials && userDataStr) {
      try {
        const userData = JSON.parse(userDataStr);
        setUser(userData);
        setIsLoading(false);
        return true;
      } catch (error) {
        console.error("Erro ao parsear dados do usuário do localStorage:", error);
        logout(); // Limpa em caso de erro
        setIsLoading(false);
        return false;
      }
    } else {
      setUser(null);
      setIsLoading(false);
      return false;
    }
  };

  // Função de login
  const login = async (email: string, password: string): Promise<User | null> => {
    setIsLoading(true);
    try {
      const response = await axiosApiInstance.post("/api/auth/login", {
        email: email,
        password: password // Adicionando o password ao corpo da requisição
      });

      if (response.status === 200 && response.data && response.data.user) {
        const userData: User = response.data.user;
        localStorage.setItem("userCredentials", `${email}:${password}`); // Armazena as credenciais para o interceptor
        localStorage.setItem("userData", JSON.stringify(userData));
        setUser(userData);
        setIsLoading(false);
        return userData;
      } else {
        // Tratar casos onde o login não foi bem-sucedido mas não lançou erro (ex: status 200 mas sem dados de usuário)
        console.error("Login falhou: dados do usuário não retornados ou status inesperado", response);
        logout(); // Limpa qualquer estado anterior
        setIsLoading(false);
        return null;
      }
    } catch (error: any) {
      console.error("Erro detalhado ao fazer login:", error);
      logout(); // Limpa o estado em caso de erro
      setIsLoading(false);
      // Lança o erro para ser tratado pelo chamador (ex: formulário de login)
      // O interceptor de resposta em api.ts já lida com o redirecionamento para 401.
      throw error;
    }
  };

  // Função de logout
  const logout = () => {
    localStorage.removeItem("userCredentials");
    localStorage.removeItem("userData");
    setUser(null);
    // O interceptor do axiosApiInstance continuará tentando pegar "userCredentials",
    // mas não encontrará, então não adicionará o header Auth.
    // Redirecionar para a página de login pode ser feito aqui ou no componente que chama o logout.
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user && !!localStorage.getItem("userCredentials"), // Autenticado se tiver usuário E credenciais
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
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
}

