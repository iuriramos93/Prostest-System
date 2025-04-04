import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import axios from "axios";

// Interface para os erros
interface Erro {
  id: string;
  codigo: string;
  tipo: string;
  descricao: string;
  dataOcorrencia: string;
  status: "PENDENTE" | "EM_ANALISE" | "RESOLVIDO";
  documento: string;
  solucao?: string;
  observacoes?: string;
}

// Interface para o filtro
interface FiltroErro {
  codigo?: string;
  tipo?: string;
  dataInicial?: string;
  dataFinal?: string;
  status?: string;
}

export function Erros() {
  const [erros, setErros] = useState<Erro[]>([]);
  const [filtros, setFiltros] = useState<FiltroErro>({});
  const [isLoading, setIsLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedErro, setSelectedErro] = useState<Erro | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const { toast } = useToast();
  const { user } = useAuth();
  
  const api = axios.create({
    baseURL: "/api",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`
    }
  });

  // Carregar erros
  const carregarErros = async () => {
    setIsLoading(true);
    try {
      const response = await api.get("/erros", {
        params: {
          ...filtros,
          page,
          per_page: 10
        }
      });
      setErros(response.data.items);
      setTotalPages(Math.ceil(response.data.total / 10));
    } catch (error) {
      toast({
        title: "Erro ao carregar erros",
        description: "Ocorreu um erro ao carregar os erros. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    carregarErros();
  }, [page, filtros]);

  // Atualizar erro
  const atualizarErro = async (id: string, dados: Partial<Erro>) => {
    try {
      await api.put(`/erros/${id}`, dados);
      toast({
        title: "Erro atualizado",
        description: "O erro foi atualizado com sucesso."
      });
      carregarErros();
      setModalOpen(false);
    } catch (error) {
      toast({
        title: "Erro ao atualizar",
        description: "Ocorreu um erro ao atualizar. Tente novamente.",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "RESOLVIDO":
        return "text-green-500";
      case "EM_ANALISE":
        return "text-yellow-500";
      case "PENDENTE":
        return "text-red-500";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Análise de Erros</h1>
        <p className="text-muted-foreground">Gerencie e resolva os erros do sistema.</p>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Código do erro"
              value={filtros.codigo || ""}
              onChange={(e) => setFiltros({ ...filtros, codigo: e.target.value })}
            />
            <Select
              value={filtros.tipo}
              onValueChange={(value) => setFiltros({ ...filtros, tipo: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="VALIDACAO">Validação</SelectItem>
                <SelectItem value="PROCESSAMENTO">Processamento</SelectItem>
                <SelectItem value="INTEGRACAO">Integração</SelectItem>
                <SelectItem value="SISTEMA">Sistema</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={filtros.status}
              onValueChange={(value) => setFiltros({ ...filtros, status: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PENDENTE">Pendente</SelectItem>
                <SelectItem value="EM_ANALISE">Em Análise</SelectItem>
                <SelectItem value="RESOLVIDO">Resolvido</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <Input
              type="date"
              value={filtros.dataInicial || ""}
              onChange={(e) => setFiltros({ ...filtros, dataInicial: e.target.value })}
            />
            <Input
              type="date"
              value={filtros.dataFinal || ""}
              onChange={(e) => setFiltros({ ...filtros, dataFinal: e.target.value })}
            />
          </div>
          <div className="flex justify-end space-x-2 mt-4">
            <Button
              variant="outline"
              onClick={() => setFiltros({})}
            >
              Limpar
            </Button>
            <Button
              onClick={() => carregarErros()}
              disabled={isLoading}
            >
              Buscar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Erros */}
      <Card>
        <CardHeader>
          <CardTitle>Erros</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Código</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {erros.map((erro) => (
                <TableRow key={erro.id}>
                  <TableCell>{erro.codigo}</TableCell>
                  <TableCell>{erro.tipo}</TableCell>
                  <TableCell>{erro.descricao}</TableCell>
                  <TableCell>
                    {new Date(erro.dataOcorrencia).toLocaleDateString('pt-BR')}
                  </TableCell>
                  <TableCell>
                    <span className={getStatusColor(erro.status)}>
                      {erro.status.replace("_", " ")}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedErro(erro);
                        setModalOpen(true);
                      }}
                    >
                      Detalhes
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {erros.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-4">
                    Nenhum erro encontrado.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Paginação */}
          <div className="flex justify-center space-x-2 mt-4">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page === totalPages}
              onClick={() => setPage(page + 1)}
            >
              Próxima
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Modal de Detalhes */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Detalhes do Erro</DialogTitle>
            <DialogDescription>
              Visualize e atualize as informações do erro.
            </DialogDescription>
          </DialogHeader>

          {selectedErro && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const dados = {
                  status: formData.get("status") as Erro["status"],
                  solucao: formData.get("solucao") as string,
                  observacoes: formData.get("observacoes") as string,
                };

                atualizarErro(selectedErro.id, dados);
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <label className="text-sm font-medium">Código</label>
                <Input value={selectedErro.codigo} disabled />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Tipo</label>
                <Input value={selectedErro.tipo} disabled />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Descrição</label>
                <Textarea value={selectedErro.descricao} disabled />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Status</label>
                <Select
                  name="status"
                  defaultValue={selectedErro.status}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PENDENTE">Pendente</SelectItem>
                    <SelectItem value="EM_ANALISE">Em Análise</SelectItem>
                    <SelectItem value="RESOLVIDO">Resolvido</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Solução</label>
                <Textarea
                  name="solucao"
                  placeholder="Descreva a solução aplicada"
                  defaultValue={selectedErro.solucao}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Observações</label>
                <Textarea
                  name="observacoes"
                  placeholder="Adicione observações relevantes"
                  defaultValue={selectedErro.observacoes}
                />
              </div>

              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setModalOpen(false)}
                >
                  Cancelar
                </Button>
                <Button type="submit">
                  Salvar
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}