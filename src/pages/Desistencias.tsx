import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";

// Interface for withdrawal request
interface SolicitacaoDesistencia {
  id: string;
  numeroTitulo: string;
  protocolo: string;
  devedor: string;
  valor: string;
  data: string;
  motivo: string;
  status: "Aprovada" | "Pendente" | "Rejeitada";
}

export function Desistencias() {
  // Search form state
  const [numeroTituloBusca, setNumeroTituloBusca] = useState("");
  const [protocoloBusca, setProtocoloBusca] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  // Submission form state
  const [numeroTitulo, setNumeroTitulo] = useState("");
  const [protocolo, setProtocolo] = useState("");
  const [devedor, setDevedor] = useState("");
  const [valor, setValor] = useState("");
  const [motivo, setMotivo] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // History state
  const [solicitacoes, setSolicitacoes] = useState<SolicitacaoDesistencia[]>([
    {
      id: "1",
      numeroTitulo: "12345678",
      protocolo: "PROT-2023-001234",
      devedor: "Empresa ABC Ltda",
      valor: "R$ 1.500,00",
      data: "2023-10-05",
      motivo: "Pagamento direto ao credor",
      status: "Aprovada"
    }
  ]);

  const { toast } = useToast();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);
    
    // Simulate API search
    setTimeout(() => {
      // Here you would make an API call to search for the title
      // For now, we'll just simulate finding a title
      if (numeroTituloBusca === "12345678" || protocoloBusca === "PROT-2023-001234") {
        setNumeroTitulo("12345678");
        setProtocolo("PROT-2023-001234");
        setDevedor("Empresa ABC Ltda");
        setValor("R$ 1.500,00");
      } else {
        toast({
          title: "Título não encontrado",
          description: "Verifique os dados informados e tente novamente.",
          variant: "destructive",
        });
      }
      setIsSearching(false);
    }, 1000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!numeroTitulo || !protocolo || !devedor || !valor || !motivo) {
      toast({
        title: "Erro de validação",
        description: "Por favor, preencha todos os campos obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call to submit the withdrawal request
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Add to local state (in a real app, this would come from the API response)
      const novaSolicitacao: SolicitacaoDesistencia = {
        id: (solicitacoes.length + 1).toString(),
        numeroTitulo,
        protocolo,
        devedor,
        valor,
        data: new Date().toISOString().split('T')[0],
        motivo,
        status: "Pendente"
      };
      
      setSolicitacoes([novaSolicitacao, ...solicitacoes]);
      
      toast({
        title: "Solicitação enviada com sucesso",
        description: `A solicitação de desistência para o título ${numeroTitulo} foi enviada.`,
      });
      
      // Reset form
      setNumeroTitulo("");
      setProtocolo("");
      setDevedor("");
      setValor("");
      setMotivo("");
      setObservacoes("");
    } catch (error) {
      toast({
        title: "Erro ao enviar solicitação",
        description: "Ocorreu um erro ao enviar a solicitação. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Aprovada":
        return "text-green-500 dark:text-green-400";
      case "Pendente":
        return "text-yellow-500 dark:text-yellow-400";
      case "Rejeitada":
        return "text-red-500 dark:text-red-400";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">SISTEMA DE PROTESTO</h1>
        <h2 className="text-xl">Solicitações de Desistência</h2>
        <p className="text-muted-foreground">Envie pedidos de desistência de protesto.</p>
      </div>
      
      {/* Search Form */}
      <Card>
        <CardHeader>
          <CardTitle>Buscar Título para Desistência</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Input 
                  placeholder="Número do Título" 
                  value={numeroTituloBusca}
                  onChange={(e) => setNumeroTituloBusca(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Input 
                  placeholder="Digite o protocolo" 
                  value={protocoloBusca}
                  onChange={(e) => setProtocoloBusca(e.target.value)}
                />
              </div>
            </div>
            <Button type="submit" disabled={isSearching}>
              {isSearching ? "Buscando..." : "Buscar"}
            </Button>
          </form>
        </CardContent>
      </Card>
      
      {/* Submission Form */}
      <Card>
        <CardHeader>
          <CardTitle>Formulário de Solicitação</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Número do Título</label>
                <Input 
                  value={numeroTitulo}
                  onChange={(e) => setNumeroTitulo(e.target.value)}
                  readOnly={!!numeroTituloBusca}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Protocolo</label>
                <Input 
                  value={protocolo}
                  onChange={(e) => setProtocolo(e.target.value)}
                  readOnly={!!protocoloBusca}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome do Devedor</label>
                <Input 
                  value={devedor}
                  onChange={(e) => setDevedor(e.target.value)}
                  readOnly={!!numeroTituloBusca || !!protocoloBusca}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Valor</label>
                <Input 
                  value={valor}
                  onChange={(e) => setValor(e.target.value)}
                  readOnly={!!numeroTituloBusca || !!protocoloBusca}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Motivo da Desistência</label>
              <Select value={motivo} onValueChange={setMotivo}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione um motivo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Pagamento direto ao credor">Pagamento direto ao credor</SelectItem>
                  <SelectItem value="Acordo entre as partes">Acordo entre as partes</SelectItem>
                  <SelectItem value="Erro no envio do título">Erro no envio do título</SelectItem>
                  <SelectItem value="Duplicidade de protesto">Duplicidade de protesto</SelectItem>
                  <SelectItem value="Outros">Outros</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Observações</label>
              <Textarea 
                placeholder="Adicione informações relevantes sobre a solicitação"
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
              />
            </div>
            
            <Button type="submit" disabled={isSubmitting} className="w-full md:w-auto">
              {isSubmitting ? "Enviando..." : "Enviar Solicitação"}
            </Button>
          </form>
        </CardContent>
      </Card>
      
      {/* History */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Solicitações</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número</TableHead>
                <TableHead>Devedor</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Motivo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {solicitacoes.map((solicitacao) => (
                <TableRow key={solicitacao.id}>
                  <TableCell>{solicitacao.numeroTitulo}</TableCell>
                  <TableCell>{solicitacao.devedor}</TableCell>
                  <TableCell>{new Date(solicitacao.data).toLocaleDateString('pt-BR')}</TableCell>
                  <TableCell className={getStatusColor(solicitacao.status)}>
                    {solicitacao.status}
                  </TableCell>
                  <TableCell>{solicitacao.motivo}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}