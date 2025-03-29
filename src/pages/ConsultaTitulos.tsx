
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Eye } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useNavigate } from "react-router-dom";

// Interface para o título
interface Titulo {
  id: string;
  numero: string;
  data: string;
  valor: string;
  status: string;
  devedor: string;
  credor: string;
}

export function ConsultaTitulos() {
  const [numero, setNumero] = useState("");
  const [data, setData] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [openDetails, setOpenDetails] = useState(false);
  const [selectedTitulo, setSelectedTitulo] = useState<Titulo | null>(null);
  const navigate = useNavigate();
  
  // Mock para os títulos
  const [titulos, setTitulos] = useState<Titulo[]>([
    {
      id: "1",
      numero: "TIT-12345",
      data: "2023-10-10",
      valor: "R$ 1.500,00",
      status: "Protestado",
      devedor: "João Silva",
      credor: "Empresa XYZ"
    },
    {
      id: "2",
      numero: "TIT-12346",
      data: "2023-10-11",
      valor: "R$ 2.300,00",
      status: "Pendente",
      devedor: "Maria Souza",
      credor: "Empresa ABC"
    },
    {
      id: "3",
      numero: "TIT-12347",
      data: "2023-10-12",
      valor: "R$ 850,00",
      status: "Pago",
      devedor: "Carlos Santos",
      credor: "Empresa DEF"
    }
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulando busca
    setTimeout(() => {
      // Aqui seria feita a busca na API
      setIsLoading(false);
    }, 1000);
  };

  const handleViewDetails = (titulo: Titulo) => {
    navigate(`/titulo/${titulo.id}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Protestado":
        return "text-red-500 font-medium";
      case "Pendente":
        return "text-yellow-500 font-medium";
      case "Pago":
        return "text-green-500 font-medium";
      default:
        return "text-gray-500 font-medium";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Consulta de Títulos</h1>
        <p className="text-muted-foreground">Consulte os títulos disponíveis.</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input 
                placeholder="Número do título" 
                value={numero}
                onChange={(e) => setNumero(e.target.value)}
              />
              <Input 
                type="date" 
                value={data}
                onChange={(e) => setData(e.target.value)}
              />
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            // Inside the table component, in the TableBody section
            <TableBody>
              {titulos.map((titulo) => (
                <TableRow key={titulo.id}>
                  <TableCell>{titulo.numero}</TableCell>
                  <TableCell>{new Date(titulo.data).toLocaleDateString('pt-BR')}</TableCell>
                  <TableCell>{titulo.valor}</TableCell>
                  <TableCell>
                    <span className={getStatusColor(titulo.status)}>
                      {titulo.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => handleViewDetails(titulo)}
                      className="flex items-center gap-1"
                    >
                      <Eye className="h-4 w-4" />
                      Detalhes
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* Modal para detalhes do título */}
      <Dialog open={openDetails} onOpenChange={setOpenDetails}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Detalhes do Título</DialogTitle>
            <DialogDescription>
              Informações completas sobre o título.
            </DialogDescription>
          </DialogHeader>
          
          {selectedTitulo && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Número</p>
                  <p className="font-medium">{selectedTitulo.numero}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Data</p>
                  <p className="font-medium">{new Date(selectedTitulo.data).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Valor</p>
                  <p className="font-medium">{selectedTitulo.valor}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <p className={`font-medium ${getStatusColor(selectedTitulo.status)}`}>
                    {selectedTitulo.status}
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Devedor</p>
                  <p className="font-medium">{selectedTitulo.devedor}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Credor</p>
                  <p className="font-medium">{selectedTitulo.credor}</p>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button>Baixar PDF</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
