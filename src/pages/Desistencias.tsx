import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/use-auth";
import axios from "axios";

// Interface para a desistência
interface Desistencia {
  id: string;
  numeroTitulo: string;
  protocolo: string;
  devedor: string;
  valor: number;
  dataProtocolo: string;
  dataSolicitacao: string;
  motivo: string;
  observacoes?: string;
  status: "PENDENTE" | "APROVADA" | "REJEITADA";
}

// Interface para o filtro
interface FiltroDesistencia {
  numeroTitulo?: string;
  protocolo?: string;
  dataInicial?: string;
  dataFinal?: string;
  status?: string;
}

export function Desistencias() {
  const [desistencias, setDesistencias] = useState<Desistencia[]>([]);
  const [filtros, setFiltros] = useState<FiltroDesistencia>({});
  const [isLoading, setIsLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedDesistencia, setSelectedDesistencia] = useState<Desistencia | null>(null);
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

  // Carregar desistências
  const carregarDesistencias = async () => {
    setIsLoading(true);
    try {
      const response = await api.get("/desistencias", {
        params: {
          ...filtros,
          page,
          per_page: 10
        }
      });
      setDesistencias(response.data.items);
      setTotalPages(Math.ceil(response.data.total / 10));
    } catch (error) {
      toast({
        title: "Erro ao carregar desistências",
        description: "Ocorreu um erro ao carregar as desistências. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    carregarDesistencias();
  }, [page, filtros]);

  // Criar nova desistência
  const criarDesistencia = async (dados: Partial<Desistencia>) => {
    try {
      await api.post("/desistencias", dados);
      toast({
        title: "Desistência criada",
        description: "A solicitação de desistência foi criada com sucesso."
      });
      carregarDesistencias();
      setModalOpen(false);
    } catch (error) {
      toast({
        title: "Erro ao criar desistência",
        description: "Ocorreu um erro ao criar a desistência. Tente novamente.",
        variant: "destructive",
      });
    }
  };

  // Atualizar desistência
  const atualizarDesistencia = async (id: string, dados: Partial<Desistencia>) => {
    try {
      await api.put(`/desistencias/${id}`, dados);
      toast({
        title: "Desistência atualizada",
        description: "A solicitação de desistência foi atualizada com sucesso."
      });
      carregarDesistencias();
      setModalOpen(false);
    } catch (error) {
      toast({
        title: "Erro ao atualizar desistência",
        description: "Ocorreu um erro ao atualizar a desistência. Tente novamente.",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "APROVADA":
        return "text-green-500";
      case "PENDENTE":
        return "text-yellow-500";
      case "REJEITADA":
        return "text-red-500";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Desistências de Protesto</h1>
        <p className="text-muted-foreground">Gerencie as solicitações de desistência de protesto.</p>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Número do Título"
              value={filtros.numeroTitulo || ""}
              onChange={(e) => setFiltros({ ...filtros, numeroTitulo: e.target.value })}
            />
            <Input
              placeholder="Protocolo"
              value={filtros.protocolo || ""}
              onChange={(e) => setFiltros({ ...filtros, protocolo: e.target.value })}
            />
            <Select
              value={filtros.status}
              onValueChange={(value) => setFiltros({ ...filtros, status: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PENDENTE">Pendente</SelectItem>
                <SelectItem value="APROVADA">Aprovada</SelectItem>
                <SelectItem value="REJEITADA">Rejeitada</SelectItem>
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
              onClick={() => carregarDesistencias()}
              disabled={isLoading}
            >
              Buscar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Desistências */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Desistências</CardTitle>
          <Button onClick={() => {
            setSelectedDesistencia(null);
            setModalOpen(true);
          }}>
            Nova Desistência
          </Button>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número do Título</TableHead>
                <TableHead>Protocolo</TableHead>
                <TableHead>Devedor</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Data Solicitação</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {desistencias.map((desistencia) => (
                <TableRow key={desistencia.id}>
                  <TableCell>{desistencia.numeroTitulo}</TableCell>
                  <TableCell>{desistencia.protocolo}</TableCell>
                  <TableCell>{desistencia.devedor}</TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(desistencia.valor)}
                  </TableCell>
                  <TableCell>
                    {new Date(desistencia.dataSolicitacao).toLocaleDateString('pt-BR')}
                  </TableCell>
                  <TableCell>
                    <span className={getStatusColor(desistencia.status)}>
                      {desistencia.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedDesistencia(desistencia);
                        setModalOpen(true);
                      }}
                    >
                      Editar
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
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

      {/* Modal de Criação/Edição */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {selectedDesistencia ? "Editar Desistência" : "Nova Desistência"}
            </DialogTitle>
            <DialogDescription>
              {selectedDesistencia
                ? "Edite os dados da solicitação de desistência."
                : "Preencha os dados para criar uma nova solicitação de desistência."}
            </DialogDescription>
          </DialogHeader>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const dados = {
                numeroTitulo: formData.get("numeroTitulo") as string,
                protocolo: formData.get("protocolo") as string,
                devedor: formData.get("devedor") as string,
                valor: parseFloat(formData.get("valor") as string),
                motivo: formData.get("motivo") as string,
                observacoes: formData.get("observacoes") as string,
              };

              if (selectedDesistencia) {
                atualizarDesistencia(selectedDesistencia.id, dados);
              } else {
                criarDesistencia(dados);
              }
            }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Número do Título</label>
                <Input
                  name="numeroTitulo"
                  defaultValue={selectedDesistencia?.numeroTitulo}
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Protocolo</label>
                <Input
                  name="protocolo"
                  defaultValue={selectedDesistencia?.protocolo}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Devedor</label>
              <Input
                name="devedor"
                defaultValue={selectedDesistencia?.devedor}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Valor</label>
              <Input
                name="valor"
                type="number"
                step="0.01"
                defaultValue={selectedDesistencia?.valor}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Motivo</label>
              <Textarea
                name="motivo"
                defaultValue={selectedDesistencia?.motivo}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Observações</label>
              <Textarea
                name="observacoes"
                defaultValue={selectedDesistencia?.observacoes}
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
                {selectedDesistencia ? "Salvar" : "Criar"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}