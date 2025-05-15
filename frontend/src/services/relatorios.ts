import { api } from "./api";

export interface Relatorio {
  id: number;
  nome: string;
  descricao: string;
  tipo: string;
  parametros: any;
  data_criacao: string;
  usuario_id: number;
}

export interface RelatorioFiltro {
  tipo?: string;
  data_inicio?: string;
  data_fim?: string;
  status?: string;
}

export interface DashboardData {
  titulos_por_status: Record<string, number>;
  remessas_por_mes: Array<{ mes: string; quantidade: number }>;
  valor_total_protestado: number;
  taxa_sucesso_processamento: number;
}

class RelatoriosService {
  async listarRelatorios(filtros?: RelatorioFiltro) {
    try {
      const response = await api.get("/api/relatorios", { params: filtros });
      return response.data;
    } catch (error: any) {
      console.error("Erro ao listar relatórios:", error);
      // Lógica de fallback para dados simulados foi removida.
      // O erro agora será lançado para ser tratado pelo componente que chamou esta função.
      throw error;
    }
  }

  async gerarRelatorio(id: number, parametros: any) {
    try {
      const response = await api.post(`/api/relatorios/${id}/gerar`, parametros);
      return response.data;
    } catch (error) {
      console.error("Erro ao gerar relatório:", error);
      throw error;
    }
  }

  async downloadRelatorio(id: number) {
    try {
      const response = await api.get(`/api/relatorios/${id}/download`, {
        responseType: "blob"
      });
      return response.data;
    } catch (error) {
      console.error("Erro ao baixar relatório:", error);
      throw error;
    }
  }

  async criarRelatorio(relatorio: Partial<Relatorio>) {
    try {
      const response = await api.post("/api/relatorios", relatorio);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar relatório:", error);
      throw error;
    }
  }

  async atualizarRelatorio(id: number, relatorio: Partial<Relatorio>) {
    try {
      const response = await api.put(`/api/relatorios/${id}`, relatorio);
      return response.data;
    } catch (error) {
      console.error("Erro ao atualizar relatório:", error);
      throw error;
    }
  }

  async excluirRelatorio(id: number) {
    try {
      await api.delete(`/api/relatorios/${id}`);
    } catch (error) {
      console.error("Erro ao excluir relatório:", error);
      throw error;
    }
  }
}

export const relatoriosService = new RelatoriosService();

