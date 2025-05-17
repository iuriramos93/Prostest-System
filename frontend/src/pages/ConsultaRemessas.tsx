import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Eye, Download, FileSpreadsheet, FilePdf, FileText } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import { api } from "@/services/api";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useNavigate } from "react-router-dom";

// Definir interface para a remessa
interface Remessa {
  id: number;
  nome_arquivo: string;
  data_envio: string;
  status: string;
  uf: string;
  tipo: string;
  quantidade_titulos: number;
}

// Interface para metadados de paginação
interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
  next_page: number | null;
  prev_page: number | null;
}

// Interface para resposta paginada
interface PaginatedResponse {
  items: Remessa[];
  meta: PaginationMeta;
}

export function ConsultaRemessas() {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [numero, setNumero] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [status, setStatus] = useState("");
  const [uf, setUf] = useState("");
  const [tipo, setTipo] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [remessas, setRemessas] = useState<Remessa[]>([]);
  const [paginationMeta, setPaginationMeta] = useState<PaginationMeta>({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false,
    next_page: null,
    prev_page: null
  });

  // Carregar remessas ao iniciar o componente
  useEffect(() => {
    carregarRemessas();
  }, []);

  // Função para carregar remessas com filtros e paginação
  const carregarRemessas = async (page = 1) => {
    setIsLoading(true);
    try {
      // Construir parâmetros de consulta
      const params = new URLSearchParams();
      if (tipo) params.append('tipo', tipo);
      if (uf) params.append('uf', uf);
      if (status) params.append('status', status);
      if (dataInicio) params.append('dataInicio', dataInicio);
      if (dataFim) params.append('dataFim', dataFim);
      params.append('page', page.toString());
      params.append('per_page', '10');

      // Fazer requisição à API
      const response = await api.get<PaginatedResponse>(`/api/remessas?${params.toString()}`);
      setRemessas(response.data.items);
      setPaginationMeta(response.data.meta);
    } catch (error) {
      console.error("Erro ao carregar remessas:", error);
      toast({
        title: "Erro",
        description: "Não foi possível carregar as remessas. Tente novamente mais tarde.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Função para lidar com a busca
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    carregarRemessas(1); // Resetar para a primeira página ao buscar
  };

  // Função para navegar para os detalhes da remessa
  const verDetalhes = (id: number) => {
    navigate(`/remessas/${id}`);
  };

  // Função para exportar remessas
  const exportarRemessas = async (formato: string) => {
    setIsExporting(true);
    try {
      // Construir parâmetros de consulta (mesmos filtros da busca)
      const params = new URLSearchParams();
      if (tipo) params.append('tipo', tipo);
      if (uf) params.append('uf', uf);
      if (status) params.append('status', status);
      if (dataInicio) params.append('dataInicio', dataInicio);
      if (dataFim) params.append('dataFim', dataFim);

      // URL base para exportação
      let url = `/api/remessas/exportar?${params.toString()}`;
      
      // Ajustar URL conforme o formato
      if (formato === 'csv') {
        // Usar a rota já implementada no backend
        window.open(`${api.defaults.baseURL}${url}`, '_blank');
      } else {
        // Para outros formatos, mostrar mensagem de que será implementado
        toast({
          title: "Em desenvolvimento",
          description: `A exportação para ${formato.toUpperCase()} será implementada em breve.`,
          variant: "default"
        });
      }
    } catch (error) {
      console.error(`Erro ao exportar para ${formato}:`, error);
      toast({
        title: "Erro na exportação",
        description: `Não foi possível exportar para ${formato.toUpperCase()}. Tente novamente mais tarde.`,
        variant: "destructive"
      });
    } finally {
      setIsExporting(false);
    }
  };

  // Função para obter a cor do status
  const getStatusColor = (status: string) => {
    switch (status) {
      case "Processado":
        return "text-green-500 dark:text-green-400";
      case "Pendente":
        return "text-yellow-500 dark:text-yellow-400";
      case "Erro":
        return "text-red-500 dark:text-red-400";
      default:
        return "";
    }
  };

  // Renderizar páginas para paginação
  const renderPaginationItems = () => {
    const items = [];
    const maxVisiblePages = 5;
    const currentPage = paginationMeta.page;
    const totalPages = paginationMeta.pages;
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      items.push(
        <PaginationItem key={i}>
          <PaginationLink
            isActive={i === currentPage}
            onClick={() => carregarRemessas(i)}
          >
            {i}
          </PaginationLink>
        </PaginationItem>
      );
    }
    
    return items;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Consulta de Remessas</h1>
          <p className="text-muted-foreground">Pesquise e acompanhe suas remessas.</p>
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button disabled={isExporting || remessas.length === 0}>
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => exportarRemessas('csv')}>
              <FileText className="mr-2 h-4 w-4" />
              <span>CSV</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => exportarRemessas('excel')}>
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              <span>Excel</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => exportarRemessas('pdf')}>
              <FilePdf className="mr-2 h-4 w-4" />
              <span>PDF</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Tipo</label>
                <Select value={tipo} onValueChange={setTipo}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    <SelectItem value="Remessa">Remessa</SelectItem>
                    <SelectItem value="Desistência">Desistência</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-1 block">UF</label>
                <Input 
                  placeholder="UF" 
                  value={uf}
                  onChange={(e) => setUf(e.target.value)}
                  maxLength={2}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-1 block">Status</label>
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    <SelectItem value="Processado">Processado</SelectItem>
                    <SelectItem value="Pendente">Pendente</SelectItem>
                    <SelectItem value="Erro">Erro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-1 block">Data Início</label>
                <Input 
                  type="date" 
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-1 block">Data Fim</label>
                <Input 
                  type="date" 
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                />
              </div>
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Buscando..." : "Buscar"}
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Resultados ({paginationMeta.total} remessas encontradas)</CardTitle>
        </CardHeader>
        <CardContent>
          {remessas.length > 0 ? (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome do arquivo</TableHead>
                    <TableHead>Data de envio</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>UF</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Qtd. Títulos</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {remessas.map((remessa) => (
                    <TableRow key={remessa.id}>
                      <TableCell>{remessa.nome_arquivo}</TableCell>
                      <TableCell>{new Date(remessa.data_envio).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell className={getStatusColor(remessa.status)}>
                        {remessa.status}
                      </TableCell>
                      <TableCell>{remessa.uf}</TableCell>
                      <TableCell>{remessa.tipo}</TableCell>
                      <TableCell>{remessa.quantidade_titulos}</TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          size="icon" 
                          onClick={() => verDetalhes(remessa.id)}
                          title="Ver detalhes"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {/* Paginação */}
              {paginationMeta.pages > 1 && (
                <div className="mt-4 flex justify-center">
                  <Pagination>
                    <PaginationContent>
                      {paginationMeta.has_prev && (
                        <PaginationItem>
                          <PaginationPrevious 
                            onClick={() => carregarRemessas(paginationMeta.prev_page || 1)} 
                          />
                        </PaginationItem>
                      )}
                      
                      {renderPaginationItems()}
                      
                      {paginationMeta.has_next && (
                        <PaginationItem>
                          <PaginationNext 
                            onClick={() => carregarRemessas(paginationMeta.next_page || paginationMeta.page + 1)} 
                          />
                        </PaginationItem>
                      )}
                    </PaginationContent>
                  </Pagination>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Nenhuma remessa encontrada.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
