
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

// Interface para o usuário
interface User {
  id: string;
  name: string;
  email: string;
}

// Interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
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
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('token');

      if (storedUser && token) {
        setUser(JSON.parse(storedUser));
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Função de login
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    
    try {
      // Simulação de API para login
      // Na versão real, isso seria substituído por uma chamada real à API
      return new Promise<void>((resolve, reject) => {
        setTimeout(() => {
          // Verifica credenciais (mock)
          if (email === 'admin@example.com' && password === 'admin123') {
            const userData = {
              id: '1',
              name: 'Administrador',
              email: 'admin@example.com'
            };
            
            // Salva o token e os dados do usuário (simulado)
            localStorage.setItem('token', 'mock-jwt-token');
            localStorage.setItem('user', JSON.stringify(userData));
            
            setUser(userData);
            setIsLoading(false);
            resolve();
          } else {
            setIsLoading(false);
            reject(new Error('Credenciais inválidas'));
          }
        }, 1000);
      });
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  // Função de logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout
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
