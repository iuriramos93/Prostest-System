// Serviço de API com cache para o Sistema de Protesto
import axios from 'axios';
import useSWR, { SWRConfiguration } from 'swr';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Configuração do axios com token
const getAuthHeader = () => {
  const token = localStorage.getItem("token");
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

// Fetcher padrão para SWR
const fetcher = async (url: string) => {
  const response = await axios.get(`${API_URL}${url}`, getAuthHeader());
  return response.data;
};

// Configuração padrão do SWR
const defaultConfig: SWRConfiguration = {
  revalidateOnFocus: false,  // Não revalidar ao focar na janela
  revalidateOnReconnect: true,  // Revalidar ao reconectar
  refreshInterval: 0,  // Não revalidar automaticamente
  shouldRetryOnError: true,  // Tentar novamente em caso de erro
  errorRetryCount: 3,  // Número máximo de tentativas
  dedupingInterval: 2000,  // Intervalo para deduplicação de requisições
};

/**
 * Hook para buscar dados com cache
 * 
 * @param endpoint Endpoint da API (sem a URL base)
 * @param config Configuração do SWR
 * @returns Dados, erro e estado de carregamento
 */
export const useApiData = <T>(endpoint: string, config?: SWRConfiguration) => {
  const { data, error, isLoading, mutate } = useSWR<T>(
    endpoint,
    fetcher,
    { ...defaultConfig, ...config }
  );

  return {
    data,
    isLoading,
    isError: !!error,
    error,
    mutate, // Função para revalidar manualmente os dados
  };
};

/**
 * Hook para buscar dados com debounce para inputs de busca
 * 
 * @param endpoint Endpoint base da API
 * @param query Termo de busca
 * @param config Configuração do SWR
 * @returns Dados, erro e estado de carregamento
 */
export const useSearchData = <T>(endpoint: string, query: string, config?: SWRConfiguration) => {
  // Só faz a requisição se a query tiver pelo menos 3 caracteres
  const shouldFetch = query.length >= 3;
  const { data, error, isLoading, mutate } = useSWR<T>(
    shouldFetch ? `${endpoint}?q=${encodeURIComponent(query)}` : null,
    fetcher,
    { ...defaultConfig, ...config }
  );

  return {
    data,
    isLoading: shouldFetch && isLoading,
    isError: !!error,
    error,
    mutate,
  };
};

// Serviço para remessas com cache
export const remessaServiceWithCache = {
  // Listar remessas com cache
  useRemessas: (filtros?: any, config?: SWRConfiguration) => {
    const queryParams = filtros ? `?${new URLSearchParams(filtros).toString()}` : '';
    return useApiData(`/api/remessas${queryParams}`, config);
  },
  
  // Obter detalhes de uma remessa com cache
  useRemessaDetalhes: (id: string | number, config?: SWRConfiguration) => {
    return useApiData(`/api/remessas/${id}`, config);
  },
  
  // Enviar uma nova remessa (sem cache, pois é uma operação de escrita)
  enviarRemessa: async (formData: FormData) => {
    try {
      const response = await axios.post(`${API_URL}/api/remessas`, formData, {
        ...getAuthHeader(),
        headers: {
          ...getAuthHeader().headers,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao enviar remessa:", error);
      throw error;
    }
  },
};

// Serviço para títulos com cache
export const tituloServiceWithCache = {
  // Listar títulos com cache e paginação
  useTitulos: (page = 1, perPage = 20, filtros?: any, config?: SWRConfiguration) => {
    const params = new URLSearchParams(filtros || {});
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    
    return useApiData(`/api/titulos?${params.toString()}`, config);
  },
  
  // Obter detalhes de um título com cache
  useTituloDetalhes: (id: string | number, config?: SWRConfiguration) => {
    return useApiData(`/api/titulos/${id}`, config);
  },
  
  // Buscar títulos com debounce
  useBuscarTitulos: (termo: string, config?: SWRConfiguration) => {
    return useSearchData('/api/titulos/buscar', termo, config);
  },
};

// Serviço para dashboard com dados agregados
export const dashboardServiceWithCache = {
  // Obter dados do dashboard (agregados para reduzir múltiplas chamadas)
  useDashboardData: (config?: SWRConfiguration) => {
    return useApiData('/api/dashboard', {
      ...config,
      // Revalidar a cada 5 minutos
      refreshInterval: 5 * 60 * 1000,
    });
  },
};

// Exportar todos os serviços
export {
  fetcher,
  API_URL,
};