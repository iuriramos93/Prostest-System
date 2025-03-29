
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Eye } from "lucide-react";

// Definir interface para a remessa
interface Remessa {
  id: string;
  arquivo: string;
  data: string;
  status: "Processado" | "Pendente" | "Erro";
  uf: string;
}

export function ConsultaRemessas() {
  const [numero, setNumero] = useState("");
  const [data, setData] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [remessas, setRemessas] = useState<Remessa[]>([
    {
      id: "1",
      arquivo: "remessa_20231010.xml",
      data: "2023-10-10",
      status: "Processado",
      uf: "SP"
    },
    {
      id: "2",
      arquivo: "remessa_20231011.xml",
      data: "2023-10-11",
      status: "Pendente",
      uf: "RJ"
    },
    {
      id: "3",
      arquivo: "remessa_20231012.xml",
      data: "2023-10-12",
      status: "Erro",
      uf: "MG"
    }
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulando busca
    setTimeout(() => {
      // Aqui seria feita a busca na API
      // Por enquanto apenas simulamos o resultado
      setIsLoading(false);
    }, 1000);
  };

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Consulta de Remessas</h1>
        <p className="text-muted-foreground">Pesquise e acompanhe suas remessas.</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input 
                placeholder="Número da remessa" 
                value={numero}
                onChange={(e) => setNumero(e.target.value)}
              />
              <Input 
                type="date" 
                value={data}
                onChange={(e) => setData(e.target.value)}
              />
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos</SelectItem>
                  <SelectItem value="Processado">Processado</SelectItem>
                  <SelectItem value="Pendente">Pendente</SelectItem>
                  <SelectItem value="Erro">Erro</SelectItem>
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
              {remessas.map((remessa) => (
                <TableRow key={remessa.id}>
                  <TableCell>{remessa.arquivo}</TableCell>
                  <TableCell>{new Date(remessa.data).toLocaleDateString('pt-BR')}</TableCell>
                  <TableCell className={getStatusColor(remessa.status)}>
                    {remessa.status}
                  </TableCell>
                  <TableCell>{remessa.uf}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="icon">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
