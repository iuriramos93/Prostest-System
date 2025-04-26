import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const ErrosService = {
  listarErros: async (filtros: { codigo?: string; status?: string; dataInicio?: string; dataFim?: string; page?: number; per_page?: number }) => {
    try {
      const response = await axios.get(`${API_URL}/erros`, {
        params: filtros,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar erros:', error);
      throw error;
    }
  },

  resolverErro: async (id: string, solucao: string) => {
    try {
      const response = await axios.put(
        `${API_URL}/erros/${id}`,
        { solucao, status: 'Resolvido' },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao resolver erro:', error);
      throw error;
    }
  }
};