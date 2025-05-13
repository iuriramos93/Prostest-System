import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Download, FileText, FileSpreadsheet, Printer, Share2, Clock, AlertTriangle } from "lucide-react";

interface Titulo {
  id: string;
  numero: string;
  data: string;
  valor: string;
  status: string;
  devedor: string;
  credor: string;
  vencimento: string;
  apresentante: string;
  cartorio: string;
  protocolo: string;
  historico: {
    data: string;
    status: string;
    descricao: string;
  }[];
}

export function DetalhesTitulo() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [titulo, setTitulo] = useState<Titulo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulação de carregamento de dados
    const fetchTitulo = async () => {
      setIsLoading(true);
      try {
        // Simulando uma chamada à API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Dados mockados
        setTitulo({
          id: id || "1",
          numero: "TIT-12345",
          data: "2023-10-10",
          valor: "R$ 1.500,00",
          status: "Protestado",
          devedor: "João Silva",
          credor: "Empresa XYZ",
          vencimento: "2023-09-30",
          apresentante: "Banco ABC",
          cartorio: "1º Cartório de Protestos",
          protocolo: "PROT-98765",
          historico: [
            {
              data: "2023-10-10",
              status: "Protestado",
              descricao: "Título protestado por falta de pagamento"
            },
            {
              data: "2023-10-05",
              status: "Em processamento",
              descricao: "Título enviado para cartório"
            },
            {
              data: "2023-10-01",
              status: "Pendente",
              descricao: "Título registrado no sistema"
            }
          ]
        });
      } catch (error) {
        toast({
          title: "Erro ao carregar dados",
          description: "Não foi possível carregar os detalhes do título.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchTitulo();
  }, [id, toast]);

  const handleDownload = (format: string) => {
    toast({
      title: "Download iniciado",
      description: `Os detalhes do título estão sendo baixados no formato ${format.toUpperCase()}.`,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Protestado":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
      case "Pendente":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300";
      case "Pago":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "Em processamento":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Clock className="h-10 w-10 text-muted-foreground mx-auto mb-4 animate-pulse" />
          <p className="text-muted-foreground">Carregando detalhes do título...</p>
        </div>
      </div>
    );
  }

  if (!titulo) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-10 w-10 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Título não encontrado</h2>
          <p className="text-muted-foreground mb-4">Não foi possível encontrar os detalhes do título solicitado.</p>
          <Button onClick={() => navigate("/consulta-titulos")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para Consulta
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => navigate("/consulta-titulos")}
            className="mb-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para Consulta
          </Button>
          <h1 className="text-2xl font-bold">Detalhes do Título</h1>
          <p className="text-muted-foreground">Informações completas do título {titulo.numero}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={() => handleDownload("pdf")}>
            <FileText className="mr-2 h-4 w-4" />
            PDF
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleDownload("excel")}>
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            Excel
          </Button>
          <Button variant="outline" size="sm" onClick={() => window.print()}>
            <Printer className="mr-2 h-4 w-4" />
            Imprimir
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Compartilhar
          </Button>
        </div>
      </div>
      
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Informações Gerais</CardTitle>
            <Badge className={getStatusColor(titulo.status)}>
              {titulo.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Número do Título</p>
                <p className="font-medium">{titulo.numero}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data de Emissão</p>
                <p className="font-medium">{new Date(titulo.data).toLocaleDateString('pt-BR')}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data de Vencimento</p>
                <p className="font-medium">{new Date(titulo.vencimento).toLocaleDateString('pt-BR')}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Valor</p>
                <p className="font-medium">{titulo.valor}</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Devedor</p>
                <p className="font-medium">{titulo.devedor}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Credor</p>
                <p className="font-medium">{titulo.credor}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Apresentante</p>
                <p className="font-medium">{titulo.apresentante}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Cartório</p>
                <p className="font-medium">{titulo.cartorio}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Tabs defaultValue="historico">
        <TabsList>
          <TabsTrigger value="historico">Histórico</TabsTrigger>
          <TabsTrigger value="documentos">Documentos</TabsTrigger>
          <TabsTrigger value="anotacoes">Anotações</TabsTrigger>
        </TabsList>
        
        <TabsContent value="historico" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Histórico do Título</CardTitle>
              <CardDescription>Acompanhe a evolução do título no sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {titulo.historico.map((item, index) => (
                  <div key={index} className="relative pl-6 pb-6 border-l border-gray-200 dark:border-gray-700">
                    {index !== titulo.historico.length - 1 && (
                      <div className="absolute bottom-0 left-0 w-6 border-b border-gray-200 dark:border-gray-700"></div>
                    )}
                    <div className="absolute top-0 left-0 -translate-x-1/2 w-3 h-3 rounded-full bg-primary"></div>
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium">{new Date(item.data).toLocaleDateString('pt-BR')}</p>
                        <Badge className={getStatusColor(item.status)}>
                          {item.status}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground">{item.descricao}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="documentos" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Documentos Relacionados</CardTitle>
              <CardDescription>Documentos vinculados a este título</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Instrumento de Protesto</h3>
                      <p className="text-sm text-muted-foreground">Emitido em: 10/10/2023</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </div>
                
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Notificação ao Devedor</h3>
                      <p className="text-sm text-muted-foreground">Emitido em: 05/10/2023</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </div>
                
                <div className="border rounded-md p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">Título Original</h3>
                      <p className="text-sm text-muted-foreground">Emitido em: 01/10/2023</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="anotacoes" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Anotações</CardTitle>
              <CardDescription>Observações e anotações sobre este título</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-md p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium">Tentativa de contato com devedor</h3>
                    <p className="text-sm text-muted-foreground">08/10/2023</p>
                  </div>
                  <p className="text-sm">Realizada tentativa de contato telefônico com o devedor, sem sucesso. Enviado e-mail solicitando retorno.</p>
                </div>
                
                <div className="border rounded-md p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium">Verificação de endereço</h3>
                    <p className="text-sm text-muted-foreground">03/10/2023</p>
                  </div>
                  <p className="text-sm">Confirmado endereço do devedor para envio da notificação.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}