// Serviço de API para o Sistema de Protesto
import axios from 'axios';

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

// Serviço para remessas
export const remessaService = {
  // Enviar uma nova remessa
  enviarRemessa: async (formData: FormData) => {
    try {
      const response = await axios.post(`${API_URL}/remessas`, formData, {
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

  // Listar remessas
  listarRemessas: async (filtros?: any) => {
    try {
      const response = await axios.get(`${API_URL}/remessas`, {
        ...getAuthHeader(),
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao listar remessas:", error);
      throw error;
    }
  },

  // Obter detalhes de uma remessa
  obterRemessa: async (id: string) => {
    try {
      const response = await axios.get(`${API_URL}/remessas/${id}`, getAuthHeader());
      return response.data;
    } catch (error) {
      console.error(`Erro ao obter remessa ${id}:`, error);
      throw error;
    }
  }
};

// Serviço para desistências
export const desistenciaService = {
  // Enviar uma nova desistência
  enviarDesistencia: async (formData: FormData) => {
    try {
      const response = await axios.post(`${API_URL}/desistencias`, formData, {
        ...getAuthHeader(),
        headers: {
          ...getAuthHeader().headers,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao enviar desistência:", error);
      throw error;
    }
  },

  // Listar desistências
  listarDesistencias: async (filtros?: any) => {
    try {
      // Tentar fazer a requisição ao servidor
      const response = await axios.get(`${API_URL}/desistencias`, {
        ...getAuthHeader(),
        params: filtros
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao listar desistências:", error);
      
      // Se o servidor não estiver disponível, retornar dados simulados
      if (error.code === 'ERR_NETWORK') {
        console.log('Servidor indisponível, usando dados simulados');
        
        // Dados simulados para desenvolvimento
        const dadosSimulados = {
          items: [
            {
              id: '1',
              numeroTitulo: '12345678',
              protocolo: 'PROT-001',
              devedor: 'Empresa ABC Ltda',
              valor: 1500.75,
              dataProtocolo: '2023-10-15',
              dataSolicitacao: '2023-10-20',
              motivo: 'Pagamento realizado',
              status: 'PENDENTE'
            },
            {
              id: '2',
              numeroTitulo: '87654321',
              protocolo: 'PROT-002',
              devedor: 'João da Silva',
              valor: 850.00,
              dataProtocolo: '2023-09-10',
              dataSolicitacao: '2023-09-25',
              motivo: 'Acordo entre as partes',
              observacoes: 'Cliente entrou em contato',
              status: 'APROVADA'
            },
            {
              id: '3',
              numeroTitulo: '45678912',
              protocolo: 'PROT-003',
              devedor: 'Comércio XYZ',
              valor: 3200.50,
              dataProtocolo: '2023-11-05',
              dataSolicitacao: '2023-11-10',
              motivo: 'Título com erro',
              status: 'REJEITADA'
            }
          ],
          total: 3
        };
        
        return dadosSimulados;
      }
      
      throw error;
    }
  }
};

// Exportar outros serviços conforme necessário
export default {
  remessaService,
  desistenciaService
};