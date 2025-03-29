import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, FileText, CheckCircle, Search, AlertTriangle } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";

// Interface para os erros
interface Erro {
  id: string;
  codigo: string;
  descricao: string;
  data: string;
  status: "Pendente" | "Resolvido";
  documento: string;
  solucao?: string;
}

export function AnaliseErros() {
  const [erros, setErros] = useState<Erro[]>([
    {
      id: "1",
      codigo: "ERR-001",
      descricao: "Documento inválido",
      data: "2023-10-10",
      status: "Pendente",
      documento: "remessa_20231010.xml"
    },
    {
      id: "2",
      codigo: "ERR-002",
      descricao: "Assinatura digital ausente",
      data: "2023-10-11",
      status: "Pendente",
      documento: "remessa_20231011.xml"
    },
    {
      id: "3",
      codigo: "ERR-003",
      descricao: "Formato de data incorreto",
      data: "2023-10-12",
      status: "Resolvido",
      documento: "remessa_20231012.xml",
      solucao: "Corrigido o formato da data para DD/MM/AAAA"
    }
  ]);

  const [filtro, setFiltro] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedErro, setSelectedErro] = useState<Erro | null>(null);
  const [solucao, setSolucao] = useState("");
  const { toast } = useToast();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulando busca
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  const handleResolverErro = (erro: Erro) => {
    setSelectedErro(erro);
    setSolucao("");
    setOpenDialog(true);
  };

  const handleSalvarSolucao = () => {
    if (!selectedErro || !solucao) {
      toast({
        title: "Erro",
        description: "Por favor, informe uma solução para o erro.",
        variant: "destructive",
      });
      return;
    }

    // Atualiza o erro com a solução
    const updatedErros = erros.map(erro => {
      if (erro.id === selectedErro.id) {
        return {
          ...erro,
          status: "Resolvido" as const,
          solucao: solucao
        };
      }
      return erro;
    });

    setErros(updatedErros);
    setOpenDialog(false);
    
    toast({
      title: "Sucesso",
      description: `O erro ${selectedErro.codigo} foi marcado como resolvido.`,
    });
  };

  const filteredErros = erros.filter(erro => {
    if (status && erro.status !== status) return false;
    if (filtro && !erro.codigo.includes(filtro) && !erro.descricao.toLowerCase().includes(filtro.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Análise de Erros</h1>
        <p className="text-muted-foreground">Revise e resolva os erros encontrados.</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input 
                placeholder="Código ou descrição do erro" 
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
              />
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="Pendente">Pendente</SelectItem>
                  <SelectItem value="Resolvido">Resolvido</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Buscando..." : "Buscar"}
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Resultados</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="pendentes">
            <TabsList className="mb-4">
              <TabsTrigger value="pendentes">Pendentes</TabsTrigger>
              <TabsTrigger value="resolvidos">Resolvidos</TabsTrigger>
              <TabsTrigger value="todos">Todos</TabsTrigger>
            </TabsList>
            
            <TabsContent value="pendentes">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Ação</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredErros.filter(erro => erro.status === "Pendente").map((erro) => (
                    <TableRow key={erro.id}>
                      <TableCell className="font-medium">{erro.codigo}</TableCell>
                      <TableCell>{erro.descricao}</TableCell>
                      <TableCell>{new Date(erro.data).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>{erro.documento}</TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          onClick={() => handleResolverErro(erro)}
                        >
                          Resolver
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredErros.filter(erro => erro.status === "Pendente").length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-4">
                        Nenhum erro pendente encontrado.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TabsContent>
            
            <TabsContent value="resolvidos">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Solução</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredErros.filter(erro => erro.status === "Resolvido").map((erro) => (
                    <TableRow key={erro.id}>
                      <TableCell className="font-medium">{erro.codigo}</TableCell>
                      <TableCell>{erro.descricao}</TableCell>
                      <TableCell>{new Date(erro.data).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>{erro.documento}</TableCell>
                      <TableCell>{erro.solucao}</TableCell>
                    </TableRow>
                  ))}
                  {filteredErros.filter(erro => erro.status === "Resolvido").length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-4">
                        Nenhum erro resolvido encontrado.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TabsContent>
            
            <TabsContent value="todos">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Ação</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredErros.map((erro) => (
                    <TableRow key={erro.id}>
                      <TableCell className="font-medium">{erro.codigo}</TableCell>
                      <TableCell>{erro.descricao}</TableCell>
                      <TableCell>{new Date(erro.data).toLocaleDateString('pt-BR')}</TableCell>
                      <TableCell>
                        <span className={erro.status === "Resolvido" ? "text-green-500" : "text-yellow-500"}>
                          {erro.status}
                        </span>
                      </TableCell>
                      <TableCell>{erro.documento}</TableCell>
                      <TableCell>
                        {erro.status === "Pendente" ? (
                          <Button 
                            variant="outline" 
                            onClick={() => handleResolverErro(erro)}
                          >
                            Resolver
                          </Button>
                        ) : (
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className="text-muted-foreground"
                            onClick={() => {
                              setSelectedErro(erro);
                              setSolucao(erro.solucao || "");
                              setOpenDialog(true);
                            }}
                          >
                            Ver solução
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredErros.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-4">
                        Nenhum erro encontrado.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* Modal para resolver erro */}
      <Dialog open={openDialog} onOpenChange={setOpenDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {selectedErro?.status === "Resolvido" ? "Solução do Erro" : "Resolver Erro"}
            </DialogTitle>
            <DialogDescription>
              {selectedErro?.status === "Resolvido" 
                ? "Detalhes da solução aplicada." 
                : "Informe a solução aplicada para resolver o erro."}
            </DialogDescription>
          </DialogHeader>
          
          {selectedErro && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Código</p>
                  <p className="font-medium">{selectedErro.codigo}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Data</p>
                  <p className="font-medium">{new Date(selectedErro.data).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground">Descrição</p>
                <p className="font-medium">{selectedErro.descricao}</p>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground">Documento</p>
                <p className="font-medium">{selectedErro.documento}</p>
              </div>
              
              {selectedErro.status === "Resolvido" ? (
                <div>
                  <p className="text-sm text-muted-foreground">Solução</p>
                  <p className="font-medium">{selectedErro.solucao}</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <label htmlFor="solucao" className="text-sm text-muted-foreground">
                    Solução
                  </label>
                  <Input
                    id="solucao"
                    value={solucao}
                    onChange={(e) => setSolucao(e.target.value)}
                    placeholder="Descreva a solução aplicada"
                  />
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                {selectedErro.status !== "Resolvido" && (
                  <Button onClick={handleSalvarSolucao}>
                    Marcar como resolvido
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}