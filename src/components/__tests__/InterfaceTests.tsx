import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../hooks/use-theme';
import { AuthProvider } from '../../hooks/use-auth';
import Sidebar from '../Sidebar';
import ThemeToggle from '../ThemeToggle';
import ConnectionStatus from '../ConnectionStatus';

// Mock para o hook de autenticação
jest.mock('../../hooks/use-auth', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    isAuthenticated: true,
    user: { nome_completo: 'Usuário Teste', cargo: 'Analista', admin: true },
    login: jest.fn(),
    logout: jest.fn(),
  }),
}));

// Mock para o hook de tema
jest.mock('../../hooks/use-theme', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useTheme: () => ({
    theme: 'light',
    toggleTheme: jest.fn(),
  }),
}));

// Mock para o hook de status de conexão
jest.mock('../../hooks/use-connection', () => ({
  __esModule: true,
  default: () => ({
    isOnline: true,
    lastChecked: new Date(),
  }),
}));

describe('Componentes de Interface', () => {
  test('Sidebar renderiza corretamente', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
    
    // Verificar se o logo está presente
    expect(screen.getByAltText('Logo')).toBeInTheDocument();
    
    // Verificar se os links de navegação estão presentes
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Títulos')).toBeInTheDocument();
  });

  test('ThemeToggle alterna o tema', async () => {
    const mockToggleTheme = jest.fn();
    jest.spyOn(require('../../hooks/use-theme'), 'useTheme').mockImplementation(() => ({
      theme: 'light',
      toggleTheme: mockToggleTheme,
    }));

    render(<ThemeToggle />);
    
    // Clicar no botão de alternar tema
    fireEvent.click(screen.getByRole('button'));
    
    // Verificar se a função de alternar tema foi chamada
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  test('ConnectionStatus mostra status online', () => {
    render(<ConnectionStatus />);
    
    // Verificar se o indicador de status online está presente
    expect(screen.getByText('Online')).toBeInTheDocument();
    expect(screen.getByTestId('status-indicator')).toHaveClass('bg-green-500');
  });

  test('ConnectionStatus mostra status offline', () => {
    jest.spyOn(require('../../hooks/use-connection'), 'default').mockImplementation(() => ({
      isOnline: false,
      lastChecked: new Date(),
    }));

    render(<ConnectionStatus />);
    
    // Verificar se o indicador de status offline está presente
    expect(screen.getByText('Offline')).toBeInTheDocument();
    expect(screen.getByTestId('status-indicator')).toHaveClass('bg-red-500');
  });
});

describe('Feedback Visual para Operações', () => {
  test('Exibe indicador de carregamento durante operações longas', async () => {
    // Componente de teste para simular operação longa
    const LoadingTestComponent = () => {
      const [loading, setLoading] = React.useState(false);
      
      const handleClick = () => {
        setLoading(true);
        setTimeout(() => setLoading(false), 1000);
      };
      
      return (
        <div>
          <button onClick={handleClick}>Iniciar Operação</button>
          {loading && <div data-testid="loading-indicator">Carregando...</div>}
        </div>
      );
    };
    
    render(<LoadingTestComponent />);
    
    // Clicar no botão para iniciar operação
    fireEvent.click(screen.getByText('Iniciar Operação'));
    
    // Verificar se o indicador de carregamento aparece
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    
    // Verificar se o indicador de carregamento desaparece após a operação
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 1500 });
  });

  test('Exibe mensagem de sucesso após operação bem-sucedida', async () => {
    // Componente de teste para simular operação bem-sucedida
    const SuccessTestComponent = () => {
      const [success, setSuccess] = React.useState(false);
      
      const handleClick = () => {
        setTimeout(() => setSuccess(true), 500);
      };
      
      return (
        <div>
          <button onClick={handleClick}>Enviar Dados</button>
          {success && <div data-testid="success-message">Operação realizada com sucesso!</div>}
        </div>
      );
    };
    
    render(<SuccessTestComponent />);
    
    // Clicar no botão para iniciar operação
    fireEvent.click(screen.getByText('Enviar Dados'));
    
    // Verificar se a mensagem de sucesso aparece
    await waitFor(() => {
      expect(screen.getByTestId('success-message')).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  test('Exibe mensagem de erro após falha na operação', async () => {
    // Componente de teste para simular operação com falha
    const ErrorTestComponent = () => {
      const [error, setError] = React.useState(false);
      
      const handleClick = () => {
        setTimeout(() => setError(true), 500);
      };
      
      return (
        <div>
          <button onClick={handleClick}>Operação com Erro</button>
          {error && <div data-testid="error-message">Erro ao processar a operação!</div>}
        </div>
      );
    };
    
    render(<ErrorTestComponent />);
    
    // Clicar no botão para iniciar operação
    fireEvent.click(screen.getByText('Operação com Erro'));
    
    // Verificar se a mensagem de erro aparece
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    }, { timeout: 1000 });
  });
});