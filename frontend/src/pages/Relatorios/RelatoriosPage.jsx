import React, { useState, useEffect } from 'react';
import RelatoriosService from '../../services/RelatoriosService';

const RelatoriosPage = () => {
  const [tipoRelatorio, setTipoRelatorio] = useState('titulos');
  const [formato, setFormato] = useState('json');
  const [filtros, setFiltros] = useState({
    dataInicio: '',
    dataFim: '',
    status: ''
  });
  const [carregando, setCarregando] = useState(false);
  const [mensagem, setMensagem] = useState('');
  const [historico, setHistorico] = useState([]);

  // Carregar histórico de relatórios ao montar o componente
  useEffect(() => {
    carregarHistorico();
  }, []);

  // Função para carregar o histórico de relatórios
  const carregarHistorico = async () => {
    try {
      setCarregando(true);
      const response = await RelatoriosService.obterHistoricoRelatorios();
      setHistorico(response.items || []);
    } catch (error) {
      setMensagem('Erro ao carregar histórico de relatórios');
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setCarregando(false);
    }
  };

  // Função para gerar relatório
  const gerarRelatorio = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setMensagem('');

    try {
      let response;

      switch (tipoRelatorio) {
        case 'titulos':
          response = await RelatoriosService.gerarRelatorioTitulos(filtros, formato);
          break;
        case 'remessas':
          response = await RelatoriosService.gerarRelatorioRemessas(filtros, formato);
          break;
        case 'desistencias':
          response = await RelatoriosService.gerarRelatorioDesistencias(filtros, formato);
          break;
        case 'erros':
          response = await RelatoriosService.gerarRelatorioErros(filtros, formato);
          break;
        case 'financeiro':
          response = await RelatoriosService.gerarRelatorioFinanceiro(filtros, formato);
          break;
        default:
          throw new Error('Tipo de relatório inválido');
      }

      // Se for um formato para download (não JSON), criar link para download
      if (formato !== 'json') {
        const filename = `relatorio-${tipoRelatorio}-${new Date().toISOString().split('T')[0]}.${formato}`;
        RelatoriosService.downloadBlob(response, filename);
        setMensagem(`Relatório gerado com sucesso! O download deve começar automaticamente.`);
      } else {
        // Se for JSON, apenas exibir mensagem de sucesso
        setMensagem(`Relatório gerado com sucesso! ${response.resumo?.total || ''} registros encontrados.`);
      }

      // Recarregar histórico após gerar relatório
      carregarHistorico();
    } catch (error) {
      setMensagem(`Erro ao gerar relatório: ${error.message || 'Erro desconhecido'}`);
      console.error('Erro ao gerar relatório:', error);
    } finally {
      setCarregando(false);
    }
  };

  // Função para baixar um relatório do histórico
  const baixarRelatorio = async (id) => {
    try {
      setCarregando(true);
      const response = await RelatoriosService.baixarRelatorio(id, formato);
      const filename = `relatorio-${id}.${formato}`;
      RelatoriosService.downloadBlob(response, filename);
      setMensagem('Download iniciado com sucesso!');
    } catch (error) {
      setMensagem(`Erro ao baixar relatório: ${error.message || 'Erro desconhecido'}`);
      console.error('Erro ao baixar relatório:', error);
    } finally {
      setCarregando(false);
    }
  };

  // Função para lidar com mudanças nos filtros
  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prevFiltros => ({
      ...prevFiltros,
      [name]: value
    }));
  };

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Relatórios</h1>

      {/* Formulário de geração de relatórios */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>Gerar Relatório</h5>
        </div>
        <div className="card-body">
          <form onSubmit={gerarRelatorio}>
            <div className="row mb-3">
              <div className="col-md-4">
                <label htmlFor="tipoRelatorio" className="form-label">Tipo de Relatório</label>
                <select
                  id="tipoRelatorio"
                  className="form-select"
                  value={tipoRelatorio}
                  onChange={(e) => setTipoRelatorio(e.target.value)}
                  required
                >
                  <option value="titulos">Títulos</option>
                  <option value="remessas">Remessas</option>
                  <option value="desistencias">Desistências</option>
                  <option value="erros">Erros</option>
                  <option value="financeiro">Financeiro</option>
                </select>
              </div>
              <div className="col-md-4">
                <label htmlFor="formato" className="form-label">Formato</label>
                <select
                  id="formato"
                  className="form-select"
                  value={formato}
                  onChange={(e) => setFormato(e.target.value)}
                  required
                >
                  <option value="json">JSON (visualização)</option>
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                  <option value="csv">CSV</option>
                </select>
              </div>
            </div>

            <div className="row mb-3">
              <div className="col-md-4">
                <label htmlFor="dataInicio" className="form-label">Data Inicial</label>
                <input
                  type="date"
                  id="dataInicio"
                  name="dataInicio"
                  className="form-control"
                  value={filtros.dataInicio}
                  onChange={handleFiltroChange}
                />
              </div>
              <div className="col-md-4">
                <label htmlFor="dataFim" className="form-label">Data Final</label>
                <input
                  type="date"
                  id="dataFim"
                  name="dataFim"
                  className="form-control"
                  value={filtros.dataFim}
                  onChange={handleFiltroChange}
                />
              </div>
              <div className="col-md-4">
                <label htmlFor="status" className="form-label">Status</label>
                <select
                  id="status"
                  name="status"
                  className="form-select"
                  value={filtros.status}
                  onChange={handleFiltroChange}
                >
                  <option value="">Todos</option>
                  <option value="Protestado">Protestado</option>
                  <option value="Pendente">Pendente</option>
                  <option value="Aprovado">Aprovado</option>
                  <option value="Rejeitado">Rejeitado</option>
                </select>
              </div>
            </div>

            <div className="d-grid gap-2 d-md-flex justify-content-md-end">
              <button type="submit" className="btn btn-primary" disabled={carregando}>
                {carregando ? 'Gerando...' : 'Gerar Relatório'}
              </button>
            </div>
          </form>

          {mensagem && (
            <div className={`alert ${mensagem.includes('Erro') ? 'alert-danger' : 'alert-success'} mt-3`}>
              {mensagem}
            </div>
          )}
        </div>
      </div>

      {/* Histórico de relatórios */}
      <div className="card">
        <div className="card-header">
          <h5>Histórico de Relatórios</h5>
        </div>
        <div className="card-body">
          {carregando && <p>Carregando histórico...</p>}
          
          {!carregando && historico.length === 0 && (
            <p>Nenhum relatório encontrado no histórico.</p>
          )}

          {!carregando && historico.length > 0 && (
            <div className="table-responsive">
              <table className="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Data de Geração</th>
                    <th>Usuário</th>
                    <th>Filtros</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {historico.map((relatorio) => (
                    <tr key={relatorio.id}>
                      <td>{relatorio.tipo}</td>
                      <td>{new Date(relatorio.dataGeracao).toLocaleString()}</td>
                      <td>{relatorio.usuario?.nome_completo || 'N/A'}</td>
                      <td>
                        {relatorio.filtros ? (
                          <ul className="mb-0">
                            {Object.entries(relatorio.filtros).map(([chave, valor]) => (
                              <li key={chave}>{chave}: {valor || 'N/A'}</li>
                            ))}
                          </ul>
                        ) : 'Sem filtros'}
                      </td>
                      <td>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => baixarRelatorio(relatorio.id)}
                          disabled={carregando}
                        >
                          Baixar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RelatoriosPage;