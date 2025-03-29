import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Download, FileText, FileSpreadsheet, PieChart, BarChart, LineChart } from "lucide-react";

export function Relatorios() {
  const [tipoRelatorio, setTipoRelatorio] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [uf, setUf] = useState("");
  const [formato, setFormato] = useState("pdf");
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [relatorioGerado, setRelatorioGerado] = useState(false);
  const { toast } = useToast();

  const handleGerarRelatorio = (e: React.FormEvent) => {
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
    setProgress(0);
    setRelatorioGerado(false);
    
    // Simulação de geração de relatório
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsLoading(false);
          setRelatorioGerado(true);
          toast({
            title: "Relatório gerado com sucesso",
            description: `O relatório de ${tipoRelatorio} foi gerado no formato ${formato.toUpperCase()}.`,
          });
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  const handleDownload = () => {
    toast({
      title: "Download iniciado",
      description: `O relatório está sendo baixado no formato ${formato.toUpperCase()}.`,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Relatórios</h1>
        <p className="text-muted-foreground">Gere relatórios detalhados.</p>
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
                          onChange={() => setFormato("pdf")}
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
                          onChange={() => setFormato("excel")}
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
                          onChange={() => setFormato("csv")}
                          className="h-4 w-4 rounded-full border-gray-300 text-primary focus:ring-primary"
                        />
                        <label htmlFor="csv" className="text-sm">CSV</label>
                      </div>
                    </div>
                  </div>
                </div>
                
                {isLoading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Gerando relatório...</span>
                      <span>{progress}%</span>
                    </div>
                    <Progress value={progress} />
                  </div>
                )}
                
                <div className="flex space-x-4">
                  <Button type="submit" disabled={isLoading} className="w-full md:w-auto">
                    {isLoading ? "Gerando..." : "Gerar Relatório"}
                  </Button>
                  
                  {relatorioGerado && (
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={handleDownload}
                      className="w-full md:w-auto"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download
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
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Relatório de Remessas</h3>
                      <p className="text-sm text-muted-foreground">Período: 01/10/2023 - 31/10/2023</p>
                    </div>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <FileText className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileSpreadsheet className="h-4 w-4 mr-1" />
                        Excel
                      </Button>
                    </div>
                  </div>
                </div>
                
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Relatório de Títulos</h3>
                      <p className="text-sm text-muted-foreground">Período: 01/09/2023 - 30/09/2023</p>
                    </div>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <FileText className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileSpreadsheet className="h-4 w-4 mr-1" />
                        Excel
                      </Button>
                    </div>
                  </div>
                </div>
                
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Relatório Financeiro</h3>
                      <p className="text-sm text-muted-foreground">Período: 01/08/2023 - 31/08/2023</p>
                    </div>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <FileText className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileSpreadsheet className="h-4 w-4 mr-1" />
                        Excel
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="dashboard">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Remessas por Status</CardTitle>
              </CardHeader>
              <CardContent className="flex justify-center">
                <div className="h-64 w-64 flex items-center justify-center border rounded-full">
                  <PieChart className="h-12 w-12 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Títulos por Mês</CardTitle>
              </CardHeader>
              <CardContent className="flex justify-center">
                <div className="h-64 w-full flex items-center justify-center border rounded-md">
                  <BarChart className="h-12 w-12 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Evolução de Protestos</CardTitle>
              </CardHeader>
              <CardContent className="flex justify-center">
                <div className="h-64 w-full flex items-center justify-center border rounded-md">
                  <LineChart className="h-12 w-12 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}