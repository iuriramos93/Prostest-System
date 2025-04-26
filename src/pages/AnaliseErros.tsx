import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, FileText, CheckCircle, Search, AlertTriangle, Calendar } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { ErrosService } from "@/services/erros";
import { Pagination } from "@/components/ui/pagination";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

// Interface para os erros
interface Erro {
  id: string;
  codigo: string;
  mensagem: string;
  dataOcorrencia: string;
  dataResolucao?: string;
  status: "Pendente" | "Resolvido";
  solucao?: string;
  modulo: string;
  criticidade: "Baixa" | "Media" | "Alta";
  remessa?: {
    id: string;
    nome_arquivo: string;
    data_envio: string;
    status: string;
  };
  titulo?: {
    id: string;
    numero: string;
    protocolo: string;
    valor: number;
    status: string;
  };
  usuario_resolucao?: {
    id: string;
    nome_completo: string;
  };
}

interface ErrosResponse {
  items: Erro[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export function AnaliseErros() {
  const [erros, setErros] = useState<Erro[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedErro, setSelectedErro] = useState<Erro | null>(null);
  const [solucao, setSolucao] = useState("");
  const { toast } = useToast();
  
  // Filtros
  const [codigo, setCodigo] = useState("");
  const [status, setStatus] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [activeTab, setActiveTab] = useState("pendentes");
  
  // Paginação
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Carregar erros
  const carregarErros = async () => {
    setLoading(true);
    try {
      // Determinar o status baseado na tab ativa
      let statusFiltro = status;
      if (activeTab === "pendentes") {
        statusFiltro = "Pendente";
      } else if (activeTab === "resolvidos") {
        statusFiltro = "Resolvido";
      }
      
      const response = await ErrosService.listarErros({
        codigo,
        status: statusFiltro,
        dataInicio,
        dataFim,
        page,
        per_page: perPage
      });
      
      setErros(response.items);
      setTotal(response.total);
      setTotalPages(response.pages);
    } catch (error) {
      console.error("Erro ao carregar erros:", error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar os erros. Tente novamente mais tarde.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Carregar erros quando os filtros ou a página mudar
  useEffect(() => {
    carregarErros();
  }, [page, activeTab]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1); // Resetar para a primeira página ao buscar
    carregarErros();
  };

  const handleResolverErro = (erro: Erro) => {
    setSelectedErro(erro);
    setSolucao("");
    setOpenDialog(true);
  };

  const handleSalvarSolucao = async () => {
    if (!selectedErro || !solucao) {
      toast({
        title: "Erro",
        description: "Por favor, informe uma solução para o erro.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await ErrosService.resolverErro(selectedErro.id, solucao);
      
      // Atualizar a lista de erros
      carregarErros();
      setOpenDialog(false);
      
      toast({
        title: "Sucesso",
        description: `O erro ${selectedErro.codigo} foi marcado como resolvido.`,
      });
    } catch (error) {
      console.error("Erro ao resolver erro:", error);
      toast({
        title: "Erro",
        description: "Não foi possível resolver o erro. Tente novamente mais tarde.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const formatarData = (dataString: string) => {
    try {
      const data = new Date(dataString);
      return format(data, "dd/MM/yyyy HH:mm", { locale: ptBR });
    } catch (error) {
      return "Data inválida";
    }
  };

  const getCriticidadeColor = (criticidade: string) => {
    switch (criticidade) {
      case "Alta":
        return "text-red-500";
      case "Media":
        return "text-yellow-500";
      case "Baixa":
        return "text-green-500";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Análise de Erros</h1>
        <p className="text-muted-foreground">Revise e resolva os erros encontrados no sistema.</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input 
                placeholder="Código do erro" 
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
              />
              
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="Pendente">Pendente</SelectItem>
                  <SelectItem value="Resolvido">Resolvido</SelectItem>
                </SelectContent>
              </Select>
              
              <div className="flex flex-col space-y-1">
                <label className="text-sm font-medium">Data Inicial</label>
                <div className="relative">
                  <Input 
                    type="date" 
                    value={dataInicio}
                    onChange={(e) => setDataInicio(e.target.value)}
                  />
                  <Calendar className="absolute right-3 top-2.5 h-4 w-4 text-muted-foreground" />
                </div>
              </div>
              
              <div className="flex flex-col space-y-1">
                <label className="text-sm font-medium">Data Final</label>
                <div className="relative">
                  <Input 
                    type="date" 
                    value={dataFim}
                    onChange={(e) => setDataFim(e.target.value)}
                  />
                  <Calendar className="absolute right-3 top-2.5 h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Buscando..." : "Buscar"}
              <Search className="ml-2 h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Resultados</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="pendentes" value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-4">
              <TabsTrigger value="pendentes">Pendentes</TabsTrigger>
              <TabsTrigger value="resolvidos">Resolvidos</TabsTrigger>
              <TabsTrigger value="todos">Todos</TabsTrigger>
            </TabsList>
            
            <TabsContent value={activeTab}>
              {loading ? (
                <div className="flex justify-center items-center py-8">
                  <p>Carregando...</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Código</TableHead>
                        <TableHead>Mensagem</TableHead>
                        <TableHead>Data</TableHead>
                        <TableHead>Módulo</TableHead>
                        <TableHead>Criticidade</TableHead>
                        <TableHead>Ação</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {erros.length > 0 ? (
                        erros.map((erro) => (
                          <TableRow key={erro.id}>
                            <TableCell className="font-medium">{erro.codigo}</TableCell>
                            <TableCell>{erro.mensagem}</TableCell>
                            <TableCell>{formatarData(erro.dataOcorrencia)}</TableCell>
                            <TableCell>{erro.modulo}</TableCell>
                            <TableCell className={getCriticidadeColor(erro.criticidade)}>
                              {erro.criticidade}
                            </TableCell>
                            <TableCell>
                              {erro.status === "Pendente" ? (
                                <Button 
                                  variant="outline" 
                                  onClick={() => handleResolverErro(erro)}
                                >
                                  Resolver
                                </Button>
                              ) : (
                                <div className="flex items-center text-green-500">
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Resolvido
                                </div>
                              )}
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={6} className="text-center py-4">
                            Nenhum erro encontrado.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                  
                  {totalPages > 1 && (
                    <div className="flex justify-center mt-4">
                      <Pagination>
                        <Button 
                          variant="outline" 
                          onClick={() => setPage(page > 1 ? page - 1 : 1)}
                          disabled={page === 1}
                        >
                          Anterior
                        </Button>
                        <div className="mx-4 flex items-center">
                          Página {page} de {totalPages}
                        </div>
                        <Button 
                          variant="outline" 
                          onClick={() => setPage(page < totalPages ? page + 1 : totalPages)}
                          disabled={page === totalPages}
                        >
                          Próxima
                        </Button>
                      </Pagination>
                    </div>
                  )}
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* Modal para resolver erro */}
      <Dialog open={openDialog} onOpenChange={setOpenDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolver Erro</DialogTitle>
            <DialogDescription>
              Informe a solução aplicada para resolver este erro.
            </DialogDescription>
          </DialogHeader>
          
          {selectedErro && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Código:</p>
                  <p>{selectedErro.codigo}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Data:</p>
                  <p>{formatarData(selectedErro.dataOcorrencia)}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm font-medium">Mensagem:</p>
                <p>{selectedErro.mensagem}</p>
              </div>
              
              {selectedErro.remessa && (
                <div>
                  <p className="text-sm font-medium">Remessa:</p>
                  <p>{selectedErro.remessa.nome_arquivo}</p>
                </div>
              )}
              
              {selectedErro.titulo && (
                <div>
                  <p className="text-sm font-medium">Título:</p>
                  <p>Número: {selectedErro.titulo.numero}, Protocolo: {selectedErro.titulo.protocolo}</p>
                </div>
              )}
              
              <div>
                <p className="text-sm font-medium">Solução:</p>
                <Textarea 
                  placeholder="Descreva a solução aplicada..."
                  value={solucao}
                  onChange={(e) => setSolucao(e.target.value)}
                  rows={4}
                />
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpenDialog(false)}>Cancelar</Button>
            <Button onClick={handleSalvarSolucao} disabled={loading}>
              {loading ? "Salvando..." : "Salvar Solução"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}