import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { relatoriosService } from '@/services/relatorios';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface DashboardData {
  titulos_por_status: Record<string, number>;
  remessas_por_mes: Array<{ mes: string; quantidade: number }>;
  valor_total_protestado: number;
  taxa_sucesso_processamento: number;
}

interface PieChartData {
  name: string;
  value: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export function Dashboard() {
  const [data, setData] = useState<DashboardData>({
    titulos_por_status: {},
    remessas_por_mes: [],
    valor_total_protestado: 0,
    taxa_sucesso_processamento: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      const response = await relatoriosService.listarRelatorios({ tipo: 'dashboard' });
      setData(response);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatarValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarPorcentagem = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(valor / 100);
  };

  const dadosPieChart: PieChartData[] = Object.entries(data.titulos_por_status).map(([name, value]) => ({
    name,
    value
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Visão geral do sistema de protestos
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Valor Total Protestado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatarValor(data.valor_total_protestado)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Taxa de Sucesso
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatarPorcentagem(data.taxa_sucesso_processamento)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="titulos" className="space-y-4">
        <TabsList>
          <TabsTrigger value="titulos">Títulos por Status</TabsTrigger>
          <TabsTrigger value="remessas">Remessas por Mês</TabsTrigger>
        </TabsList>

        <TabsContent value="titulos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Distribuição de Títulos por Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dadosPieChart}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }: { name: string; percent: number }) => 
                        `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {dadosPieChart.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="remessas" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Remessas por Mês</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.remessas_por_mes}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="mes" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="quantidade" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
