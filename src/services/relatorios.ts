import axios from 'axios';

interface FiltrosRelatorio {
  dataInicio?: string;
  dataFim?: string;
  uf?: string;
  status?: string;
  formato: 'pdf' | 'excel' | 'csv';
  tipo: 'titulos' | 'remessas' | 'desistencias' | 'erros' | 'financeiro';
}

interface RespostaRelatorio {
  resumo: {
    total_titulos?: number;
    valor_total?: number;
    total_remessas?: number;
    data_geracao: string;
    filtros_aplicados: Record<string, string>;
  };
  dados: any[];
  url_download?: string;
}

const API_URL = import.meta.env.VITE_API_URL + '/api/relatorios' || 'http://localhost:5000/api/relatorios';

export const RelatoriosService = {
  async gerarRelatorio(
    tipo: 'titulos' | 'remessas' | 'desistencias' | 'erros' | 'financeiro',
    filtros: FiltrosRelatorio
  ): Promise<RespostaRelatorio> {
    const params = new URLSearchParams({
      data_inicio: filtros.dataInicio || '',
      data_fim: filtros.dataFim || '',
      uf: filtros.uf || '',
      status: filtros.status || '',
      formato: filtros.formato,
      tipo: filtros.tipo
    });

    const response = await axios.get(`${API_URL}/${tipo}?${params}`, {
      responseType: filtros.formato === 'pdf' ? 'blob' : 'json'
    });

    if (filtros.formato === 'pdf') {
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      return {
        resumo: {
          data_geracao: new Date().toISOString(),
          filtros_aplicados: Object.entries(filtros).reduce((acc, [key, value]) => {
            acc[key] = String(value);
            return acc;
          }, {} as Record<string, string>)
        },
        dados: [],
        url_download: url
      };
    }

    return response.data;
  },

  async obterHistoricoRelatorios(): Promise<{
    relatorios: Array<{
      id: string;
      tipo: string;
      data_geracao: string;
      formato: string;
      url_download: string;
    }>;
  }> {
    const response = await axios.get(`${API_URL}/historico`);
    return response.data;
  },

  async obterDadosDashboard(): Promise<{
    titulos_por_status: Record<string, number>;
    remessas_por_mes: Array<{ mes: string; quantidade: number }>;
    valor_total_protestado: number;
    taxa_sucesso_processamento: number;
  }> {
    try {
      const response = await axios.get(`${API_URL}/dashboard`);
      // Garantir que todos os campos esperados existam no objeto retornado
      const data = response.data || {};
      return {
        titulos_por_status: data.titulos_por_status || {},
        remessas_por_mes: data.remessas_por_mes || [],
        valor_total_protestado: data.valor_total_protestado || 0,
        taxa_sucesso_processamento: data.taxa_sucesso_processamento || 0
      };
    } catch (error) {
      console.error('Erro ao obter dados do dashboard:', error);
      // Retornar objeto vazio em caso de erro para evitar quebras na interface
      return {
        titulos_por_status: {},
        remessas_por_mes: [],
        valor_total_protestado: 0,
        taxa_sucesso_processamento: 0
      };
    }
  }
};