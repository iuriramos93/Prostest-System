import { render, act, renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../use-auth';
import axios from 'axios';

// Remove duplicate imports
//import { render, screen, fireEvent } from '@testing-library/react';

// Single axios mock definition
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }))
}));

describe('useAuth Hook', () => {
  const mockAxios = axios as jest.Mocked<typeof axios>;
  const mockApi = mockAxios.create();

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should initialize with unauthenticated user', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(result.current.isLoading).toBeTruthy();
  });

  it('should authenticate user with valid credentials', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User'
    };

    (mockApi.post as jest.Mock).mockResolvedValueOnce({
      data: { token: 'fake-token', user: mockUser }
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBeTruthy();
    expect(localStorage.getItem('token')).toBe('fake-token');
  });

  it('deve manter sessão ativa com token válido', async () => {
    localStorage.setItem('token', 'token-valido');

    const mockUser = {
      id: '1',
      email: 'teste@exemplo.com',
      nome_completo: 'Usuário Teste'
    };

    (mockAxios.get as jest.Mock).mockResolvedValueOnce({ data: mockUser });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBeTruthy();
      expect(result.current.isLoading).toBeFalsy();
    });
  });

  it('deve fazer logout corretamente', async () => {
    localStorage.setItem('token', 'token-teste');
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('deve lidar com erro de login', async () => {
    (mockAxios.post as jest.Mock).mockRejectedValueOnce(new Error('Credenciais inválidas'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    await expect(result.current.login('teste@exemplo.com', 'senha-errada'))
      .rejects.toThrow('Credenciais inválidas');

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
  });

  it('deve lidar com token inválido', async () => {
    localStorage.setItem('token', 'token-invalido');

    (mockAxios.get as jest.Mock).mockRejectedValueOnce(new Error('Token inválido'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    await waitFor(() => {
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBeFalsy();
      expect(localStorage.getItem('token')).toBeNull();
    });
  });
});