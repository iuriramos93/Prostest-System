import { api } from './api'; // Instância do Axios já configurada com interceptor Basic Auth

// Interface para as credenciais de login, embora o Basic Auth as envie via header
// O corpo da requisição de login pode ser vazio ou conter o email para identificação, dependendo do backend
export interface LoginCredentials {
  email: string;
  // A senha será usada para construir o header Basic Auth pelo useAuth e interceptor
  // password: string; // Removido daqui, pois o useAuth cuidará de pegar a senha
}

export interface User {
  id: string; // Ajustado para string, se for o caso no seu backend (ex: UUID)
  nome_completo?: string;
  name?: string; // Adicionado para consistência com use-auth
  email: string;
  username?: string;
  cargo?: string;
  admin?: boolean;
  ativo?: boolean;
  data_criacao?: string;
}

class AuthService {
  // O método login agora é mais uma formalidade para chamar o endpoint de login.
  // A lógica principal de armazenamento de credenciais e estado do usuário está no useAuth.
  // Este método pode ser usado para verificar se as credenciais são válidas e obter dados do usuário.
  async login(email: string, password: string): Promise<User | null> {
    try {
      // Armazena temporariamente as credenciais para o interceptor usar nesta chamada específica
      // Esta é uma forma de garantir que o login use as credenciais fornecidas AGORA,
      // antes que o useAuth as salve permanentemente no localStorage após o sucesso.
      const tempCredentials = `${email}:${password}`;
      const base64TempCredentials = btoa(tempCredentials);

      const response = await api.post(
        '/api/auth/login', 
        { email }, // O backend pode usar o email do corpo para identificar o usuário
        {
          headers: {
            // Sobrescreve temporariamente o Authorization para esta chamada específica de login
            // para usar as credenciais que acabaram de ser digitadas pelo usuário.
            'Authorization': `Basic ${base64TempCredentials}`
          }
        }
      );

      if (response.status === 200 && response.data && response.data.user) {
        // O useAuth.tsx será responsável por salvar as credenciais e os dados do usuário no localStorage
        // após este método retornar com sucesso.
        return response.data.user as User;
      }
      return null; // Login falhou ou não retornou usuário
    } catch (error) {
      console.error('Erro ao fazer login no authService:', error);
      // O useAuth tratará de limpar o localStorage em caso de erro no seu próprio catch block.
      throw error; // Propaga o erro para ser tratado pelo useAuth
    }
  }

  // Logout não é mais gerenciado aqui, mas sim pelo useAuth, que limpa o localStorage.
  // Esta classe pode não precisar mais de um método logout se o useAuth centralizar isso.
  // Se mantido, deve estar alinhado com o useAuth.
  logout() {
    // A lógica de limpar localStorage e redirecionar está no useAuth.logout()
    // Chamadas a este método devem ser substituídas por chamadas a useAuth().logout()
    console.warn("authService.logout() chamado. Considere usar useAuth().logout() diretamente.");
    localStorage.removeItem("userCredentials");
    localStorage.removeItem("userData");
    if (window.location.pathname !== "/login") {
        window.location.href = "/login";
    }
  }

  // Obter dados do usuário atualmente logado (se houver sessão válida com Basic Auth)
  async getCurrentUser(): Promise<User | null> {
    try {
      // O interceptor em api.ts adicionará o header Basic Auth se userCredentials existir no localStorage
      const response = await api.get('/api/auth/me'); 
      return response.data.user as User;
    } catch (error) {
      // Se der 401, o interceptor de resposta em api.ts já deve ter limpado as credenciais
      // e iniciado o redirecionamento para /login.
      console.error('Erro ao obter usuário atual (authService):', error);
      return null;
    }
  }

  // A verificação de autenticação agora é feita pelo useAuth().isAuthenticated
  // que verifica a presença de userCredentials e userData no localStorage.
  isAuthenticated(): boolean {
    // Esta lógica está duplicada/desatualizada em relação ao useAuth
    console.warn("authService.isAuthenticated() chamado. Considere usar useAuth().isAuthenticated diretamente.");
    return !!localStorage.getItem('userCredentials') && !!localStorage.getItem('userData');
  }

  // Não há mais token JWT para ser obtido.
  // getToken(): string | null {
  //   return null;
  // }
}

export const authService = new AuthService();

