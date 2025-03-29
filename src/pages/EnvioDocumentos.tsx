
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

export function EnvioDocumentos() {
  const [tipo, setTipo] = useState<string>("remessa");
  const [uf, setUf] = useState<string>("");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [descricao, setDescricao] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tipo || !uf || !arquivo) {
      toast({
        title: "Erro de validação",
        description: "Por favor, preencha todos os campos obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      // Simulação de envio para API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: "Documento enviado com sucesso",
        description: `O ${tipo} para ${uf} foi enviado.`,
      });
      
      // Limpar formulário
      setTipo("remessa");
      setUf("");
      setArquivo(null);
      setDescricao("");
    } catch (error) {
      toast({
        title: "Erro ao enviar documento",
        description: "Ocorreu um erro ao enviar o documento. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Verificando se é um arquivo XML
      if (!file.name.endsWith('.xml')) {
        toast({
          title: "Formato inválido",
          description: "Por favor, selecione um arquivo XML.",
          variant: "destructive",
        });
        e.target.value = '';
        return;
      }
      
      setArquivo(file);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Envio de Documentos</h1>
        <p className="text-muted-foreground">Envie seus documentos de remessa ou desistência aqui.</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Formulário de Envio</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="tipo">Tipo de documento</Label>
                  <Select value={tipo} onValueChange={setTipo}>
                    <SelectTrigger id="tipo">
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="remessa">Remessa</SelectItem>
                      <SelectItem value="desistencia">Desistência</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="uf">UF</Label>
                  <Select value={uf} onValueChange={setUf}>
                    <SelectTrigger id="uf">
                      <SelectValue placeholder="Selecione a UF" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="SP">São Paulo</SelectItem>
                      <SelectItem value="RJ">Rio de Janeiro</SelectItem>
                      <SelectItem value="MG">Minas Gerais</SelectItem>
                      <SelectItem value="RS">Rio Grande do Sul</SelectItem>
                      <SelectItem value="PR">Paraná</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="arquivo">Selecione o documento (XML)</Label>
                <Input 
                  id="arquivo" 
                  type="file" 
                  accept=".xml" 
                  onChange={handleFileChange}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="descricao">Descrição</Label>
                <Textarea 
                  id="descricao" 
                  placeholder="Adicione informações relevantes sobre o documento"
                  value={descricao}
                  onChange={(e) => setDescricao(e.target.value)}
                />
              </div>
            </div>
            
            <Button type="submit" disabled={isLoading} className="w-full md:w-auto">
              {isLoading ? "Enviando..." : "Enviar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
