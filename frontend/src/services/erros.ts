import { api } from './api';

export const ErrosService = {
  listarErros: async (filtros: { codigo?: string; status?: string; dataInicio?: string; dataFim?: string; page?: number; per_page?: number }) => {
    try {
      const response = await api.get(`/api/erros`, {
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar erros:', error);
      throw error;
    }
  },

  resolverErro: async (id: string, solucao: string) => {
    try {
      const response = await api.put(
        `/api/erros/${id}`,
        { solucao, status: 'Resolvido' }
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao resolver erro:', error);
      throw error;
    }
  }
};