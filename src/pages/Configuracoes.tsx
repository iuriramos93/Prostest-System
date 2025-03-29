
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Link2, Users, FileText, Settings as SettingsIcon } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";

interface Usuario {
  id: string;
  nome: string;
  email: string;
  perfil: string;
  ativo: boolean;
}

interface Log {
  id: string;
  data: string;
  tipo: "Erro" | "Informação" | "Aviso";
  usuario: string;
  mensagem: string;
}

export function Configuracoes() {
  const [activeTab, setActiveTab] = useState("integracao");
  const [usuarios, setUsuarios] = useState<Usuario[]>([
    {
      id: "1",
      nome: "Administrador",
      email: "admin@sistema.com",
      perfil: "Administrador",
      ativo: true
    },
    {
      id: "2",
      nome: "João Silva",
      email: "joao@empresa.com",
      perfil: "Operador",
      ativo: true
    },
    {
      id: "3",
      nome: "Maria Souza",
      email: "maria@empresa.com",
      perfil: "Visualizador",
      ativo: false
    }
  ]);

  const [logs, setLogs] = useState<Log[]>([
    {
      id: "1",
      data: "15/05/2023 14:32:45",
      tipo: "Erro",
      usuario: "admin@sistema.com",
      mensagem: "Falha na conexão com a API CRA-SP"
    },
    {
      id: "2",
      data: "15/05/2023 13:22:10",
      tipo: "Informação",
      usuario: "joao@empresa.com",
      mensagem: "Upload de arquivo realizado com sucesso"
    },
    {
      id: "3",
      data: "15/05/2023 11:15:33",
      tipo: "Aviso",
      usuario: "maria@empresa.com",
      mensagem: "Múltiplas tentativas de login detectadas"
    }
  ]);

  const handleSave = () => {
    toast({
      title: "Configurações salvas",
      description: "Suas configurações foram salvas com sucesso.",
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Configurações</h1>
        <p className="text-muted-foreground">Gerencie as configurações do sistema e integração CRA-SP.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-4 w-full max-w-3xl">
          <TabsTrigger value="integracao" className="flex items-center gap-2">
            <Link2 className="h-4 w-4" />
            <span className="hidden sm:inline">Integração CRA-SP</span>
            <span className="sm:hidden">Integração</span>
          </TabsTrigger>
          <TabsTrigger value="usuarios" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span className="hidden sm:inline">Usuários</span>
            <span className="sm:hidden">Usuários</span>
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span className="hidden sm:inline">Logs do Sistema</span>
            <span className="sm:hidden">Logs</span>
          </TabsTrigger>
          <TabsTrigger value="ajustes" className="flex items-center gap-2">
            <SettingsIcon className="h-4 w-4" />
            <span className="hidden sm:inline">Ajustes Gerais</span>
            <span className="sm:hidden">Ajustes</span>
          </TabsTrigger>
        </TabsList>

        {/* Integração CRA-SP */}
        <TabsContent value="integracao" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuração de API CRA-SP</CardTitle>
              <p className="text-sm text-muted-foreground">Configure as credenciais de acesso para integração com a CRA-SP.</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="apiKey">API Key</Label>
                  <Input id="apiKey" placeholder="Insira sua API Key" />
                  <p className="text-xs text-muted-foreground">Chave de acesso fornecida pela CRA-SP.</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="apiSecret">API Secret</Label>
                  <Input id="apiSecret" type="password" placeholder="Insira seu API Secret" />
                  <p className="text-xs text-muted-foreground">Senha secreta fornecida pela CRA-SP.</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="apiUrl">URL da API</Label>
                  <Input id="apiUrl" placeholder="https://api.crasp.com.br/v1" />
                  <p className="text-xs text-muted-foreground">Endpoint base da API da CRA-SP.</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timeout">Timeout (segundos)</Label>
                  <Input id="timeout" type="number" placeholder="30" />
                  <p className="text-xs text-muted-foreground">Tempo máximo de espera por resposta.</p>
                </div>
              </div>

              <div className="pt-4">
                <h3 className="text-sm font-medium mb-2">Estrutura da Base de Dados</h3>
                <div className="bg-muted p-3 rounded-md">
                  <pre className="text-xs overflow-auto whitespace-pre">
{`CREATE TABLE integracao_cra (
  id SERIAL PRIMARY KEY,
  api_key VARCHAR(255) NOT NULL,
  api_secret VARCHAR(255) NOT NULL,
  api_url VARCHAR(255) NOT NULL,
  timeout INTEGER DEFAULT 30,
  ativo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);`}
                  </pre>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Modelo da tabela para armazenar configurações de integração no PostgreSQL.
                </p>
              </div>

              <Button onClick={handleSave}>Salvar Configurações</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usuários */}
        <TabsContent value="usuarios" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Gerenciamento de Usuários</CardTitle>
                <p className="text-sm text-muted-foreground">Crie, edite e remova acessos ao sistema.</p>
              </div>
              <Button>Adicionar Usuário</Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead>Perfil</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usuarios.map((usuario) => (
                    <TableRow key={usuario.id}>
                      <TableCell>{usuario.nome}</TableCell>
                      <TableCell>{usuario.email}</TableCell>
                      <TableCell>{usuario.perfil}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${usuario.ativo ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'}`}>
                          {usuario.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                      </TableCell>
                      <TableCell className="space-x-2">
                        <Button variant="outline" size="sm">Editar</Button>
                        <Button variant="outline" size="sm" className="text-red-500 hover:text-red-700">Remover</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="pt-6">
                <h3 className="text-sm font-medium mb-2">Estrutura da Base de Dados</h3>
                <div className="bg-muted p-3 rounded-md">
                  <pre className="text-xs overflow-auto whitespace-pre">
{`CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  perfil VARCHAR(50) NOT NULL,
  ativo BOOLEAN DEFAULT TRUE,
  ultimo_acesso TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para permissões
CREATE TABLE permissoes (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  descricao TEXT
);

-- Tabela de relacionamento entre usuários e permissões
CREATE TABLE usuario_permissoes (
  usuario_id INTEGER REFERENCES usuarios(id),
  permissao_id INTEGER REFERENCES permissoes(id),
  PRIMARY KEY (usuario_id, permissao_id)
);`}
                  </pre>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Modelo relacional para sistema de usuários e permissões.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Logs do Sistema */}
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Logs do Sistema</CardTitle>
                <p className="text-sm text-muted-foreground">Histórico de atividades e eventos do sistema.</p>
              </div>
              <Button variant="outline">Exportar Logs</Button>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <Label htmlFor="dataInicio">Data Início</Label>
                  <Input id="dataInicio" type="date" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="dataFim">Data Fim</Label>
                  <Input id="dataFim" type="date" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="tipoLog">Tipo de Log</Label>
                  <Select defaultValue="todos">
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Todos os tipos" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todos">Todos os tipos</SelectItem>
                      <SelectItem value="erro">Erro</SelectItem>
                      <SelectItem value="info">Informação</SelectItem>
                      <SelectItem value="aviso">Aviso</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data/Hora</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Usuário</TableHead>
                    <TableHead>Mensagem</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{log.data}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${log.tipo === 'Erro' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100' : 
                            log.tipo === 'Aviso' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100' : 
                            'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'}`}
                        >
                          {log.tipo}
                        </span>
                      </TableCell>
                      <TableCell>{log.usuario}</TableCell>
                      <TableCell>{log.mensagem}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="pt-6">
                <h3 className="text-sm font-medium mb-2">Estrutura da Base de Dados</h3>
                <div className="bg-muted p-3 rounded-md">
                  <pre className="text-xs overflow-auto whitespace-pre">
{`CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  tipo VARCHAR(50) NOT NULL,
  mensagem TEXT NOT NULL,
  usuario_id INTEGER REFERENCES usuarios(id),
  ip_address VARCHAR(50),
  user_agent TEXT,
  data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  detalhes JSONB
);

-- Índices para otimizar consultas
CREATE INDEX idx_logs_data_hora ON logs(data_hora);
CREATE INDEX idx_logs_tipo ON logs(tipo);
CREATE INDEX idx_logs_usuario ON logs(usuario_id);`}
                  </pre>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Esquema para armazenamento e consulta eficiente de logs do sistema.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Ajustes Gerais */}
        <TabsContent value="ajustes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ajustes Gerais</CardTitle>
              <p className="text-sm text-muted-foreground">Configure parâmetros operacionais do sistema.</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="uploadLimit">Limite máximo de upload (MB)</Label>
                  <Input id="uploadLimit" type="number" placeholder="10" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="logRetention">Período de retenção de logs (dias)</Label>
                  <Input id="logRetention" type="number" placeholder="90" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notificationEmail">E-mail para notificações</Label>
                  <Input id="notificationEmail" type="email" placeholder="notifications@empresa.com" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="exportFormat">Formato padrão de exportação</Label>
                  <Select defaultValue="pdf">
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um formato" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pdf">PDF</SelectItem>
                      <SelectItem value="csv">CSV</SelectItem>
                      <SelectItem value="excel">Excel</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2 mt-4">
                <h3 className="text-sm font-medium">Notificações</h3>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox id="notifyErrors" />
                    <Label htmlFor="notifyErrors">Enviar e-mail quando houver erros no processamento</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="notifyRemessas" />
                    <Label htmlFor="notifyRemessas">Enviar e-mail para confirmação de remessas</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="notifyUpdates" />
                    <Label htmlFor="notifyUpdates">Notificar sobre atualizações do sistema</Label>
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <h3 className="text-sm font-medium mb-2">Estrutura da Base de Dados</h3>
                <div className="bg-muted p-3 rounded-md">
                  <pre className="text-xs overflow-auto whitespace-pre">
{`CREATE TABLE configuracoes (
  id SERIAL PRIMARY KEY,
  chave VARCHAR(100) UNIQUE NOT NULL,
  valor TEXT,
  descricao TEXT,
  tipo VARCHAR(50) NOT NULL,
  grupo VARCHAR(100),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserções para configurações padrão
INSERT INTO configuracoes (chave, valor, descricao, tipo, grupo) 
VALUES 
  ('limite_upload', '10', 'Limite máximo de upload em MB', 'number', 'system'),
  ('retencao_logs', '90', 'Período de retenção de logs em dias', 'number', 'system'),
  ('email_notificacoes', 'notifications@empresa.com', 'Email para notificações', 'email', 'notifications'),
  ('formato_exportacao', 'pdf', 'Formato padrão para exportação', 'select', 'exports'),
  ('notificar_erros', 'true', 'Enviar email quando houver erros', 'boolean', 'notifications'),
  ('notificar_remessas', 'true', 'Enviar email para confirmação de remessas', 'boolean', 'notifications'),
  ('notificar_atualizacoes', 'false', 'Notificar sobre atualizações do sistema', 'boolean', 'notifications');`}
                  </pre>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Tabela de configurações flexível e extensível para armazenar todos os parâmetros do sistema.
                </p>
              </div>

              <Button onClick={handleSave}>Salvar Configurações</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Seção de Informações de Tecnologias */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Tecnologias Utilizadas</CardTitle>
          <p className="text-sm text-muted-foreground">Stack tecnológica utilizada no desenvolvimento do sistema.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium mb-2">Frontend</h3>
              <ul className="space-y-1">
                <li className="text-sm">• <strong>Template Engine:</strong> Handlebars</li>
                <li className="text-sm">• <strong>Navegação:</strong> React Router</li>
                <li className="text-sm">• <strong>Gerenciamento de Estado:</strong> TanStack Query</li>
                <li className="text-sm">• <strong>API Client:</strong> Axios</li>
                <li className="text-sm">• <strong>Formulários:</strong> React Hook Form</li>
                <li className="text-sm">• <strong>Validação:</strong> Zod</li>
                <li className="text-sm">• <strong>Componentes:</strong> Shadcn UI / Radix UI</li>
                <li className="text-sm">• <strong>Documentação:</strong> Storybook</li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-2">Backend e Infraestrutura</h3>
              <ul className="space-y-1">
                <li className="text-sm">• <strong>Ambiente Local:</strong> Docker + PostgreSQL</li>
                <li className="text-sm">• <strong>Framework Backend:</strong> Python 3.11 + Django</li>
                <li className="text-sm">• <strong>API:</strong> Django Rest Framework com JWT Auth</li>
                <li className="text-sm">• <strong>Cache:</strong> Redis</li>
                <li className="text-sm">• <strong>CI/CD:</strong> GitHub Actions</li>
                <li className="text-sm">• <strong>Modelagem de Dados:</strong> PostgreSQL</li>
              </ul>
            </div>
          </div>

          <div className="pt-4">
            <h3 className="text-sm font-medium mb-2">Diagrama ER Simplificado</h3>
            <div className="bg-muted p-3 rounded-md">
              <pre className="text-xs overflow-auto whitespace-pre">
{`-- Principais Tabelas do Sistema
usuario (1) --< (N) remessa
remessa (1) --< (N) titulo
usuario (1) --< (N) logs
remessa (1) --< (N) logs
titulo (1) --< (N) logs
usuario (N) >--< (N) permissoes`}
              </pre>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              As relações entre as principais entidades do sistema seguem o diagrama acima.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
