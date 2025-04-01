
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart2, ChevronUp, ChevronDown, ArrowRight, FileText, AlertTriangle, Settings, FileUp, Search, FileBarChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useNavigate } from "react-router-dom";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function Dashboard() {
  const navigate = useNavigate();
  
  // Navigation handlers
  const goToEnvioDocumentos = () => navigate("/envio-documentos");
  const goToConsultaRemessas = () => navigate("/consulta-remessas");
  const goToConsultaTitulos = () => navigate("/consulta-titulos");
  const goToDesistencias = () => navigate("/desistencias");
  const goToRelatorios = () => navigate("/relatorios");
  const goToConfiguracoes = () => navigate("/configuracoes");
  const goToAnaliseErros = () => navigate("/analise-erros");
  
  return (
    <div className="space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">SISTEMA DE PROTESTO</h1>
        <p className="text-muted-foreground">Bem-vindo ao sistema de gerenciamento de protestos.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium">Remessas Enviadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">126</span>
              <div className="flex items-center text-green-500 dark:text-green-400">
                <ChevronUp className="h-4 w-4" />
                <span className="text-sm">12% em relação ao mês anterior</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium">Títulos Protestados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">84</span>
              <div className="flex items-center text-green-500 dark:text-green-400">
                <ChevronUp className="h-4 w-4" />
                <span className="text-sm">8% em relação ao mês anterior</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium">Erros Pendentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">7</span>
              <div className="flex items-center text-red-500 dark:text-red-400">
                <ChevronDown className="h-4 w-4" />
                <span className="text-sm">3% em relação ao mês anterior</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium">Desistências</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">15</span>
              <div className="flex items-center text-green-500 dark:text-green-400">
                <ChevronUp className="h-4 w-4" />
                <span className="text-sm">5% em relação ao mês anterior</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Seção de Acesso Rápido */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Acesso Rápido</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToEnvioDocumentos}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <FileUp className="h-8 w-8 text-blue-500" />
              <CardTitle className="text-center text-base">Envio de Arquivos</CardTitle>
              <CardDescription className="text-center text-xs">Envie arquivos de remessa ou desistência</CardDescription>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToConsultaRemessas}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <Search className="h-8 w-8 text-blue-500" />
              <CardTitle className="text-center text-base">Consulta de Remessas</CardTitle>
              <CardDescription className="text-center text-xs">Consulte os arquivos enviados</CardDescription>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToConsultaTitulos}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <FileText className="h-8 w-8 text-blue-500" />
              <CardTitle className="text-center text-base">Consulta de Títulos</CardTitle>
              <CardDescription className="text-center text-xs">Pesquise e acompanhe seus títulos</CardDescription>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToDesistencias}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
              <CardTitle className="text-center text-base">Desistências</CardTitle>
              <CardDescription className="text-center text-xs">Solicitar desistências de protesto</CardDescription>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToRelatorios}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <FileBarChart className="h-8 w-8 text-blue-500" />
              <CardTitle className="text-center text-base">Relatórios</CardTitle>
              <CardDescription className="text-center text-xs">Acesse os relatórios do sistema</CardDescription>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={goToConfiguracoes}>
            <CardContent className="p-6 flex flex-col items-center justify-center gap-2">
              <Settings className="h-8 w-8 text-blue-500" />
              <CardTitle className="text-center text-base">Configurações</CardTitle>
              <CardDescription className="text-center text-xs">Configure o sistema e usuários</CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Últimas Remessas</CardTitle>
            <Button variant="outline" size="sm" className="gap-1" onClick={goToConsultaRemessas}>
              <span>Ver todas</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome do arquivo</TableHead>
                <TableHead>Data de envio</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>UF</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>remessa_20231010.xml</TableCell>
                <TableCell>10/10/2023</TableCell>
                <TableCell className="text-green-500 dark:text-green-400">Processado</TableCell>
                <TableCell>SP</TableCell>
                <TableCell>
                  <Button variant="link" className="p-0 h-auto">Detalhes</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>desistencia_20231009.xml</TableCell>
                <TableCell>09/10/2023</TableCell>
                <TableCell className="text-green-500 dark:text-green-400">Processado</TableCell>
                <TableCell>SP</TableCell>
                <TableCell>
                  <Button variant="link" className="p-0 h-auto">Detalhes</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>remessa_20231008.xml</TableCell>
                <TableCell>08/10/2023</TableCell>
                <TableCell className="text-red-500 dark:text-red-400">Erro</TableCell>
                <TableCell>RJ</TableCell>
                <TableCell>
                  <Button variant="link" className="p-0 h-auto">Detalhes</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>remessa_20231007.xml</TableCell>
                <TableCell>07/10/2023</TableCell>
                <TableCell className="text-green-500 dark:text-green-400">Processado</TableCell>
                <TableCell>SP</TableCell>
                <TableCell>
                  <Button variant="link" className="p-0 h-auto">Detalhes</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* Seção de Alertas e Notificações */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Alertas e Notificações</h2>
        <div className="space-y-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Erro no processamento de remessa</AlertTitle>
            <AlertDescription>
              <p>O arquivo remessa_20231008.xml possui 3 títulos com dados incorretos.</p>
              <Button 
                variant="link" 
                className="p-0 h-auto mt-2" 
                onClick={goToAnaliseErros}
              >
                Ver detalhes
              </Button>
            </AlertDescription>
          </Alert>
          
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Títulos aguardando confirmação</AlertTitle>
            <AlertDescription>
              <p>5 títulos aguardam confirmação de pagamento para baixa no sistema.</p>
              <Button 
                variant="link" 
                className="p-0 h-auto mt-2" 
                onClick={goToConsultaTitulos}
              >
                Ver títulos
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </div>
  );
}
