import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Download, FileText, FileSpreadsheet, PieChart, BarChart, LineChart, Plus, Trash2, Edit2 } from "lucide-react";
import { relatoriosService, Relatorio } from "@/services/relatorios";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { toast } from 'sonner';

export function Relatorios() {
  const [relatorios, setRelatorios] = useState<Relatorio[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRelatorio, setSelectedRelatorio] = useState<Relatorio | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    tipo: '',
    parametros: {}
  });
  const { toast } = useToast();

  useEffect(() => {
    carregarRelatorios();
  }, []);

  const carregarRelatorios = async () => {
    try {
      const response = await relatoriosService.listarRelatorios();
      setRelatorios(response);
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
      toast.error('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  };

  const handleNovoRelatorio = () => {
    setSelectedRelatorio(null);
    setFormData({
      nome: '',
      descricao: '',
      tipo: '',
      parametros: {}
    });
    setOpenDialog(true);
  };

  const handleEditarRelatorio = (relatorio: Relatorio) => {
    setSelectedRelatorio(relatorio);
    setFormData({
      nome: relatorio.nome,
      descricao: relatorio.descricao,
      tipo: relatorio.tipo,
      parametros: relatorio.parametros
    });
    setOpenDialog(true);
  };

  const handleSalvarRelatorio = async () => {
    try {
      if (selectedRelatorio) {
        await relatoriosService.atualizarRelatorio(selectedRelatorio.id, formData);
        toast.success('Relatório atualizado com sucesso');
      } else {
        await relatoriosService.criarRelatorio(formData);
        toast.success('Relatório criado com sucesso');
      }
      setOpenDialog(false);
      carregarRelatorios();
    } catch (error) {
      console.error('Erro ao salvar relatório:', error);
      toast.error('Erro ao salvar relatório');
    }
  };

  const handleExcluirRelatorio = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir este relatório?')) return;
    
    try {
      await relatoriosService.excluirRelatorio(id);
      toast.success('Relatório excluído com sucesso');
      carregarRelatorios();
    } catch (error) {
      console.error('Erro ao excluir relatório:', error);
      toast.error('Erro ao excluir relatório');
    }
  };

  const handleDownloadRelatorio = async (id: number) => {
    try {
      const blob = await relatoriosService.downloadRelatorio(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Erro ao baixar relatório:', error);
      toast.error('Erro ao baixar relatório');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Relatórios</h1>
          <p className="text-muted-foreground">
            Gerencie seus relatórios personalizados
          </p>
        </div>
        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
          <DialogTrigger asChild>
            <Button onClick={() => setFormData({ nome: '', descricao: '', tipo: '', parametros: {} })}>
              Novo Relatório
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {selectedRelatorio ? 'Editar Relatório' : 'Novo Relatório'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={(e) => { e.preventDefault(); handleSalvarRelatorio(); }} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome</label>
                <Input
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  placeholder="Nome do relatório"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Descrição</label>
                <Textarea
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  placeholder="Descrição do relatório"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Tipo</label>
                <Select
                  value={formData.tipo}
                  onValueChange={(value) => setFormData({ ...formData, tipo: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dashboard">Dashboard</SelectItem>
                    <SelectItem value="titulos">Títulos</SelectItem>
                    <SelectItem value="remessas">Remessas</SelectItem>
                    <SelectItem value="desistencias">Desistências</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setOpenDialog(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {selectedRelatorio ? 'Atualizar' : 'Criar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Lista de Relatórios</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Data de Criação</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {relatorios.length > 0 ? (
                relatorios.map((relatorio) => (
                  <TableRow key={relatorio.id}>
                    <TableCell>{relatorio.nome}</TableCell>
                    <TableCell>{relatorio.tipo}</TableCell>
                    <TableCell>
                      {format(new Date(relatorio.data_criacao), 'dd/MM/yyyy HH:mm', {
                        locale: ptBR
                      })}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleDownloadRelatorio(relatorio.id)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleEditarRelatorio(relatorio)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleExcluirRelatorio(relatorio.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-4">
                    Nenhum relatório encontrado.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}