// Interface para representar um erro no sistema
export interface IErro {
  id?: string;
  codigo: string;
  mensagem: string;
  stackTrace?: string;
  dataOcorrencia: Date;
  dataResolucao?: Date;
  status: 'Pendente' | 'Resolvido';
  solucao?: string;
  modulo: string;
  criticidade: 'Baixa' | 'Media' | 'Alta';
}

// Classe para manipulação de erros no frontend
export class Erro implements IErro {
  id?: string;
  codigo: string;
  mensagem: string;
  stackTrace?: string;
  dataOcorrencia: Date;
  dataResolucao?: Date;
  status: 'Pendente' | 'Resolvido';
  solucao?: string;
  modulo: string;
  criticidade: 'Baixa' | 'Media' | 'Alta';
  
  constructor(erro: IErro) {
    this.id = erro.id;
    this.codigo = erro.codigo;
    this.mensagem = erro.mensagem;
    this.stackTrace = erro.stackTrace;
    this.dataOcorrencia = erro.dataOcorrencia;
    this.dataResolucao = erro.dataResolucao;
    this.status = erro.status;
    this.solucao = erro.solucao;
    this.modulo = erro.modulo;
    this.criticidade = erro.criticidade;
  }
}