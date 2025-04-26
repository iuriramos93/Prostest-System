import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Download, FileText, FileSpreadsheet, PieChart, BarChart, LineChart } from "lucide-react";
import { RelatoriosService } from "@/services/relatorios";

export function Relatorios() {
  const [tipoRelatorio, setTipoRelatorio] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [uf, setUf] = useState("");
  const [formato, setFormato] = useState("pdf");
  const [isLoading, setIsLoading] = useState(false);
  const [urlDownload, setUrlDownload] = useState("");
  const [dadosDashboard, setDadosDashboard] = useState<any>(null);
  const [historicoRelatorios, setHistoricoRelatorios] = useState<any[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    carregarDadosDashboard();
    carregarHistorico();
  }, []);

  const carregarDadosDashboard = async () => {
    try {
      const dados = await RelatoriosService.obterDadosDashboard();
      setDadosDashboard(dados);
    } catch (error) {
      console.error("Erro ao carregar dashboard:", error);
      setDadosDashboard({
        titulos_por_status: {},
        remessas_por_mes: [],
        valor_total_protestado: 0,
        taxa_sucesso_processamento: 0
      });
      toast({
        title: "Erro ao carregar dashboard",
        description: "Não foi possível carregar os dados do dashboard.",
        variant: "destructive",
      });
    }
  };

  const carregarHistorico = async () => {
    try {
      const { relatorios } = await RelatoriosService.obterHistoricoRelatorios();
      setHistoricoRelatorios(relatorios || []);
    } catch (error) {
      console.error("Erro ao carregar histórico:", error);
      setHistoricoRelatorios([]);
      toast({
        title: "Erro ao carregar histórico",
        description: "Não foi possível carregar o histórico de relatórios.",
        variant: "destructive",
      });
    }
  };

  const handleGerarRelatorio = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tipoRelatorio || !dataInicio || !dataFim) {
      toast({
        title: "Erro de validação",
        description: "Por favor, preencha todos os campos obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setUrlDownload("");
    
    try {
      const resposta = await RelatoriosService.gerarRelatorio(
        tipoRelatorio as any,
        {
          dataInicio,
          dataFim,
          uf,
          formato: formato as any
        }
      );

      if (resposta.url_download) {
        setUrlDownload(resposta.url_download);
      }

      toast({
        title: "Relatório gerado com sucesso",
        description: `O relatório de ${tipoRelatorio} foi gerado no formato ${formato.toUpperCase()}.`,
      });

      await carregarHistorico();
    } catch (error) {
      toast({
        title: "Erro ao gerar relatório",
        description: "Ocorreu um erro ao gerar o relatório. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (urlDownload) {
      window.open(urlDownload, '_blank');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Relatórios</h1>
        <p className="text-muted-foreground">Gere relatórios detalhados do sistema.</p>
      </div>
      
      <Tabs defaultValue="gerar" className="space-y-6">
        <TabsList>
          <TabsTrigger value="gerar">Gerar Relatório</TabsTrigger>
          <TabsTrigger value="historico">Histórico</TabsTrigger>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        </TabsList>
        
        <TabsContent value="gerar">
          <Card>
            <CardHeader>
              <CardTitle>Formulário de Geração</CardTitle>
              <CardDescription>Preencha os campos para gerar um novo relatório</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGerarRelatorio} className="space-y-6">
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label htmlFor="tipo" className="text-sm font-medium">
                        Tipo de Relatório
                      </label>
                      <Select value={tipoRelatorio} onValueChange={setTipoRelatorio}>
                        <SelectTrigger id="tipo">
                          <SelectValue placeholder="Selecione o tipo" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="remessas">Remessas</SelectItem>
                          <SelectItem value="titulos">Títulos</SelectItem>
                          <SelectItem value="desistencias">Desistências</SelectItem>
                          <SelectItem value="erros">Erros</SelectItem>
                          <SelectItem value="financeiro">Financeiro</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <label htmlFor="uf" className="text-sm font-medium">
                        UF (opcional)
                      </label>
                      <Select value={uf} onValueChange={setUf}>
                        <SelectTrigger id="uf">
                          <SelectValue placeholder="Todas" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="todas">Todas</SelectItem>
                          <SelectItem value="SP">São Paulo</SelectItem>
                          <SelectItem value="RJ">Rio de Janeiro</SelectItem>
                          <SelectItem value="MG">Minas Gerais</SelectItem>
                          <SelectItem value="RS">Rio Grande do Sul</SelectItem>
                          <SelectItem value="PR">Paraná</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label htmlFor="dataInicio" className="text-sm font-medium">
                        Data Inicial
                      </label>
                      <Input 
                        id="dataInicio" 
                        type="date" 
                        value={dataInicio}
                        onChange={(e) => setDataInicio(e.target.value)}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label htmlFor="dataFim" className="text-sm font-medium">
                        Data Final
                      </label>
                      <Input 
                        id="dataFim" 
                        type="date" 
                        value={dataFim}
                        onChange={(e) => setDataFim(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Formato de Saída
                    </label>
                    <div className="flex space-x-4">
                      <div className="flex items-center space-x-2">
                        <input 
                          type="radio" 
                          id="pdf" 
                          name="formato" 
                          value="pdf"
                          checked={formato === "pdf"}
                          onChange={(e) => setFormato(e.target.value)}
                          className="h-4 w-4 rounded-full border-gray-300 text-primary focus:ring-primary"
                        />
                        <label htmlFor="pdf" className="text-sm">PDF</label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input 
                          type="radio" 
                          id="excel" 
                          name="formato" 
                          value="excel"
                          checked={formato === "excel"}
                          onChange={(e) => setFormato(e.target.value)}
                          className="h-4 w-4 rounded-full border-gray-300 text-primary focus:ring-primary"
                        />
                        <label htmlFor="excel" className="text-sm">Excel</label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input 
                          type="radio" 
                          id="csv" 
                          name="formato" 
                          value="csv"
                          checked={formato === "csv"}
                          onChange={(e) => setFormato(e.target.value)}
                          className="h-4 w-4 rounded-full border-gray-300 text-primary focus:ring-primary"
                        />
                        <label htmlFor="csv" className="text-sm">CSV</label>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-4">
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Gerando..." : "Gerar Relatório"}
                  </Button>
                  {urlDownload && (
                    <Button type="button" variant="outline" onClick={handleDownload}>
                      <Download className="h-4 w-4 mr-2" />
                      Baixar Relatório
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historico">
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Relatórios</CardTitle>
              <CardDescription>Relatórios gerados anteriormente</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {historicoRelatorios.map((relatorio) => (
                  <div key={relatorio.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {relatorio.formato === 'pdf' ? (
                        <FileText className="h-6 w-6 text-blue-500" />
                      ) : (
                        <FileSpreadsheet className="h-6 w-6 text-green-500" />
                      )}
                      <div>
                        <p className="font-medium">{relatorio.tipo}</p>
                        <p className="text-sm text-muted-foreground">
                          Gerado em {new Date(relatorio.data_geracao).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <Button variant="ghost" onClick={() => window.open(relatorio.url_download, '_blank')}>
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                {historicoRelatorios.length === 0 && (
                  <p className="text-center text-muted-foreground">Nenhum relatório encontrado</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dashboard">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Títulos por Status</CardTitle>
              </CardHeader>
              <CardContent>
                {dadosDashboard?.titulos_por_status && (
                  <div className="space-y-4">
                    {Object.entries(dadosDashboard?.titulos_por_status || {}).map(([status, quantidade]) => (
                      <div key={status} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{status}</span>
                          <span className="text-sm text-muted-foreground">{String(quantidade)}</span>
                        </div>
                        <Progress value={Number(quantidade) / (Object.values(dadosDashboard?.titulos_por_status || {}).reduce((a: number, b: unknown) => a + Number(b), 0) || 1) * 100} />
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Remessas por Mês</CardTitle>
              </CardHeader>
              <CardContent>
                {dadosDashboard?.remessas_por_mes && (
                  <div className="space-y-4">
                    {dadosDashboard.remessas_por_mes.map((item: any) => (
                      <div key={item.mes} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm font-medium">{item.mes}</span>
                          <span className="text-sm text-muted-foreground">{String(item.quantidade)}</span>
                        </div>
                        <Progress value={(Number(item.quantidade) / Math.max(...(dadosDashboard?.remessas_por_mes?.map((i: any) => Number(i.quantidade)) || [1]))) * 100} />
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Valor Total Protestado</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {dadosDashboard?.valor_total_protestado
                    ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
                        .format(dadosDashboard.valor_total_protestado)
                    : 'R$ 0,00'}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Taxa de Sucesso no Processamento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold">
                    {dadosDashboard?.taxa_sucesso_processamento
                      ? `${(dadosDashboard.taxa_sucesso_processamento * 100).toFixed(1)}%`
                      : '0%'}
                  </div>
                  <Progress
                    value={dadosDashboard?.taxa_sucesso_processamento
                      ? Number(dadosDashboard.taxa_sucesso_processamento) * 100
                      : 0}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}