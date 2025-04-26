import axios from 'axios';
import { getAuthToken } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class RelatoriosService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/relatorios`,
    });

    // Interceptor para adicionar o token de autenticação em todas as requisições
    this.api.interceptors.request.use(
      (config) => {
        const token = getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  /**
   * Gera um relatório de títulos com base nos filtros fornecidos
   * @param {Object} filtros - Filtros para o relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv, json)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async gerarRelatorioTitulos(filtros = {}, formato = 'json') {
    try {
      const params = { ...filtros, formato };
      const response = await this.api.get('/titulos', { params, responseType: this.getResponseType(formato) });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório de títulos:', error);
      throw error;
    }
  }

  /**
   * Gera um relatório de remessas com base nos filtros fornecidos
   * @param {Object} filtros - Filtros para o relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv, json)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async gerarRelatorioRemessas(filtros = {}, formato = 'json') {
    try {
      const params = { ...filtros, formato };
      const response = await this.api.get('/remessas', { params, responseType: this.getResponseType(formato) });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório de remessas:', error);
      throw error;
    }
  }

  /**
   * Gera um relatório de desistências com base nos filtros fornecidos
   * @param {Object} filtros - Filtros para o relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv, json)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async gerarRelatorioDesistencias(filtros = {}, formato = 'json') {
    try {
      const params = { ...filtros, formato };
      const response = await this.api.get('/desistencias', { params, responseType: this.getResponseType(formato) });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório de desistências:', error);
      throw error;
    }
  }

  /**
   * Gera um relatório de erros com base nos filtros fornecidos
   * @param {Object} filtros - Filtros para o relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv, json)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async gerarRelatorioErros(filtros = {}, formato = 'json') {
    try {
      const params = { ...filtros, formato };
      const response = await this.api.get('/erros', { params, responseType: this.getResponseType(formato) });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório de erros:', error);
      throw error;
    }
  }

  /**
   * Gera um relatório financeiro com base nos filtros fornecidos
   * @param {Object} filtros - Filtros para o relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv, json)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async gerarRelatorioFinanceiro(filtros = {}, formato = 'json') {
    try {
      const params = { ...filtros, formato };
      const response = await this.api.get('/financeiro', { params, responseType: this.getResponseType(formato) });
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório financeiro:', error);
      throw error;
    }
  }

  /**
   * Obtém dados para o dashboard
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async obterDadosDashboard() {
    try {
      const response = await this.api.get('/dashboard');
      return response.data;
    } catch (error) {
      console.error('Erro ao obter dados do dashboard:', error);
      throw error;
    }
  }

  /**
   * Obtém o histórico de relatórios gerados
   * @param {Object} filtros - Filtros para o histórico
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async obterHistoricoRelatorios(filtros = {}) {
    try {
      const response = await this.api.get('/historico', { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Erro ao obter histórico de relatórios:', error);
      throw error;
    }
  }

  /**
   * Baixa um relatório específico pelo ID
   * @param {string} id - ID do relatório
   * @param {string} formato - Formato do relatório (pdf, excel, csv)
   * @returns {Promise} - Promise com o resultado da requisição
   */
  async baixarRelatorio(id, formato = 'pdf') {
    try {
      const response = await this.api.get(`/download/${id}`, {
        params: { formato },
        responseType: this.getResponseType(formato),
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao baixar relatório:', error);
      throw error;
    }
  }

  /**
   * Determina o tipo de resposta com base no formato do relatório
   * @param {string} formato - Formato do relatório
   * @returns {string} - Tipo de resposta para o axios
   */
  getResponseType(formato) {
    switch (formato.toLowerCase()) {
      case 'pdf':
      case 'excel':
      case 'csv':
        return 'blob';
      case 'json':
      default:
        return 'json';
    }
  }

  /**
   * Cria um link para download de um arquivo blob
   * @param {Blob} blob - Blob do arquivo
   * @param {string} filename - Nome do arquivo
   */
  downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
}

export default new RelatoriosService();