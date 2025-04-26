# Serviços de API

Este diretório contém os serviços responsáveis por fazer a comunicação com a API do backend.

## RelatoriosService

O `RelatoriosService` é responsável por consumir os endpoints de relatórios do backend, permitindo gerar relatórios em diferentes formatos (PDF, Excel, CSV, JSON), consultar o histórico de relatórios gerados e obter dados para o dashboard.

### Funcionalidades

- Geração de relatórios de títulos, remessas, desistências, erros e financeiro
- Download de relatórios em diferentes formatos (PDF, Excel, CSV)
- Consulta ao histórico de relatórios gerados
- Obtenção de dados para o dashboard

### Como utilizar

```javascript
import RelatoriosService from '../services/RelatoriosService';

// Exemplo de geração de relatório de títulos em formato PDF
const gerarRelatorioPDF = async () => {
  try {
    const filtros = {
      dataInicio: '2023-01-01',
      dataFim: '2023-12-31',
      status: 'Protestado'
    };
    
    const response = await RelatoriosService.gerarRelatorioTitulos(filtros, 'pdf');
    
    // Para arquivos binários (PDF, Excel, CSV), é necessário criar um link para download
    RelatoriosService.downloadBlob(response, 'relatorio-titulos.pdf');
  } catch (error) {
    console.error('Erro ao gerar relatório:', error);
  }
};

// Exemplo de obtenção de dados para o dashboard
const carregarDadosDashboard = async () => {
  try {
    const dados = await RelatoriosService.obterDadosDashboard();
    console.log('Dados do dashboard:', dados);
    // Atualizar o estado do componente com os dados recebidos
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error);
  }
};

// Exemplo de consulta ao histórico de relatórios
const consultarHistorico = async () => {
  try {
    const filtros = {
      tipoRelatorio: 'titulos',
      dataInicio: '2023-01-01',
      dataFim: '2023-12-31'
    };
    
    const historico = await RelatoriosService.obterHistoricoRelatorios(filtros);
    console.log('Histórico de relatórios:', historico);
    // Atualizar o estado do componente com o histórico recebido
  } catch (error) {
    console.error('Erro ao consultar histórico de relatórios:', error);
  }
};
```

### Métodos disponíveis

- `gerarRelatorioTitulos(filtros, formato)`: Gera relatório de títulos
- `gerarRelatorioRemessas(filtros, formato)`: Gera relatório de remessas
- `gerarRelatorioDesistencias(filtros, formato)`: Gera relatório de desistências
- `gerarRelatorioErros(filtros, formato)`: Gera relatório de erros
- `gerarRelatorioFinanceiro(filtros, formato)`: Gera relatório financeiro
- `obterDadosDashboard()`: Obtém dados para o dashboard
- `obterHistoricoRelatorios(filtros)`: Obtém histórico de relatórios gerados
- `baixarRelatorio(id, formato)`: Baixa um relatório específico pelo ID
- `downloadBlob(blob, filename)`: Utilitário para download de arquivos binários

### Formatos suportados

- `pdf`: Retorna um arquivo PDF para download
- `excel`: Retorna um arquivo Excel para download
- `csv`: Retorna um arquivo CSV para download
- `json`: Retorna os dados em formato JSON (padrão)