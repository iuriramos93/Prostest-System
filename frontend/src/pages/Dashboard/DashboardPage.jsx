import React, { useState, useEffect } from 'react';
import RelatoriosService from '../../services/RelatoriosService';

const DashboardPage = () => {
  const [dadosDashboard, setDadosDashboard] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    carregarDadosDashboard();
  }, []);

  const carregarDadosDashboard = async () => {
    try {
      setCarregando(true);
      setErro(null);
      const dados = await RelatoriosService.obterDadosDashboard();
      setDadosDashboard(dados);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      setErro('Não foi possível carregar os dados do dashboard. Tente novamente mais tarde.');
    } finally {
      setCarregando(false);
    }
  };

  if (carregando) {
    return (
      <div className="container mt-4 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Carregando...</span>
        </div>
        <p className="mt-2">Carregando dados do dashboard...</p>
      </div>
    );
  }

  if (erro) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger" role="alert">
          {erro}
          <button 
            className="btn btn-outline-danger ms-3" 
            onClick={carregarDadosDashboard}
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Dashboard</h1>

      {dadosDashboard && (
        <div className="row">
          {/* Resumo de Títulos */}
          <div className="col-md-6 col-lg-3 mb-4">
            <div className="card h-100">
              <div className="card-header bg-primary text-white">
                <h5 className="card-title mb-0">Títulos</h5>
              </div>
              <div className="card-body">
                <h3 className="card-text">{dadosDashboard.titulos?.total || 0}</h3>
                <div className="mt-3">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Protestados:</span>
                    <strong>{dadosDashboard.titulos?.protestados || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>Pendentes:</span>
                    <strong>{dadosDashboard.titulos?.pendentes || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>Pagos:</span>
                    <strong>{dadosDashboard.titulos?.pagos || 0}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Resumo de Remessas */}
          <div className="col-md-6 col-lg-3 mb-4">
            <div className="card h-100">
              <div className="card-header bg-success text-white">
                <h5 className="card-title mb-0">Remessas</h5>
              </div>
              <div className="card-body">
                <h3 className="card-text">{dadosDashboard.remessas?.total || 0}</h3>
                <div className="mt-3">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Processadas:</span>
                    <strong>{dadosDashboard.remessas?.processadas || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>Pendentes:</span>
                    <strong>{dadosDashboard.remessas?.pendentes || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>Com Erro:</span>
                    <strong>{dadosDashboard.remessas?.com_erro || 0}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Resumo de Desistências */}
          <div className="col-md-6 col-lg-3 mb-4">
            <div className="card h-100">
              <div className="card-header bg-warning text-dark">
                <h5 className="card-title mb-0">Desistências</h5>
              </div>
              <div className="card-body">
                <h3 className="card-text">{dadosDashboard.desistencias?.total || 0}</h3>
                <div className="mt-3">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Aprovadas:</span>
                    <strong>{dadosDashboard.desistencias?.aprovadas || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>Pendentes:</span>
                    <strong>{dadosDashboard.desistencias?.pendentes || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>Rejeitadas:</span>
                    <strong>{dadosDashboard.desistencias?.rejeitadas || 0}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Resumo de Erros */}
          <div className="col-md-6 col-lg-3 mb-4">
            <div className="card h-100">
              <div className="card-header bg-danger text-white">
                <h5 className="card-title mb-0">Erros</h5>
              </div>
              <div className="card-body">
                <h3 className="card-text">{dadosDashboard.erros?.total || 0}</h3>
                <div className="mt-3">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Resolvidos:</span>
                    <strong>{dadosDashboard.erros?.resolvidos || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>Pendentes:</span>
                    <strong>{dadosDashboard.erros?.pendentes || 0}</strong>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>Críticos:</span>
                    <strong>{dadosDashboard.erros?.criticos || 0}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Resumo Financeiro */}
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header bg-info text-white">
                <h5 className="card-title mb-0">Resumo Financeiro</h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <h6>Valor Total de Títulos</h6>
                    <h4>R$ {dadosDashboard.financeiro?.valor_total?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'}</h4>
                  </div>
                  <div className="col-md-6 mb-3">
                    <h6>Valor Protestado</h6>
                    <h4>R$ {dadosDashboard.financeiro?.valor_protestado?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'}</h4>
                  </div>
                  <div className="col-md-6">
                    <h6>Valor Pago</h6>
                    <h4>R$ {dadosDashboard.financeiro?.valor_pago?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'}</h4>
                  </div>
                  <div className="col-md-6">
                    <h6>Valor Pendente</h6>
                    <h4>R$ {dadosDashboard.financeiro?.valor_pendente?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'}</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Atividades Recentes */}
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header bg-secondary text-white">
                <h5 className="card-title mb-0">Atividades Recentes</h5>
              </div>
              <div className="card-body">
                {dadosDashboard.atividades_recentes && dadosDashboard.atividades_recentes.length > 0 ? (
                  <ul className="list-group list-group-flush">
                    {dadosDashboard.atividades_recentes.map((atividade, index) => (
                      <li key={index} className="list-group-item">
                        <div className="d-flex w-100 justify-content-between">
                          <h6 className="mb-1">{atividade.descricao}</h6>
                          <small>{new Date(atividade.data).toLocaleString('pt-BR')}</small>
                        </div>
                        <p className="mb-1">{atividade.detalhes}</p>
                        <small>{atividade.usuario}</small>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-center mt-3">Nenhuma atividade recente encontrada.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="d-flex justify-content-end mt-2">
        <button 
          className="btn btn-primary" 
          onClick={carregarDadosDashboard}
        >
          Atualizar Dados
        </button>
      </div>
    </div>
  );
};

export default DashboardPage;