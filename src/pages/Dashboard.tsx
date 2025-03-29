
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart2, ChevronUp, ChevronDown, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export function Dashboard() {
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
                <span className="text-sm">+12%</span>
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
                <span className="text-sm">+8%</span>
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
                <span className="text-sm">-3%</span>
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
                <span className="text-sm">+5%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Últimas Remessas</CardTitle>
            <Button variant="outline" size="sm" className="gap-1">
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
                <TableCell>remessa_20231011.xml</TableCell>
                <TableCell>11/10/2023</TableCell>
                <TableCell className="text-yellow-500 dark:text-yellow-400">Pendente</TableCell>
                <TableCell>RJ</TableCell>
                <TableCell>
                  <Button variant="link" className="p-0 h-auto">Detalhes</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
