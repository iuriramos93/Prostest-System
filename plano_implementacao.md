# Plano de Implementação para Correção de Erros

## Análise dos Problemas

Após analisar os logs de erro e os commits recentes, identifiquei dois problemas principais:

### 1. Erro de Schema do Banco de Dados
- A coluna `task_id` está definida no modelo `Remessa` mas não existe na tabela `remessas` do banco de dados
- Existe um commit específico (3bc23d4) que menciona "Migração para adicionar a coluna task_id à tabela remessas", mas parece que a migração não foi aplicada corretamente

### 2. Problemas de CORS
- Erros de CORS persistem em múltiplos endpoints (`/api/relatorios`, `/api/remessas`, `/api/desistencias`, `/api/erros`)
- Mensagem específica: "Response to preflight request doesn't pass access control check: Redirect is not allowed for a preflight request"
- Apesar do commit recente (cb386d0) "Correção permanente de CORS e integração de dados", os problemas persistem

## Plano de Implementação

### Fase 1: Correção do Schema do Banco de Dados

1. **Verificar o status da migração**
   - Examinar os arquivos de migração existentes
   - Verificar se a migração foi executada no banco de dados

2. **Corrigir o schema do banco**
   - Opção A: Aplicar a migração existente se não foi executada
   - Opção B: Criar uma nova migração para adicionar a coluna `task_id`
   - Opção C: Executar um ALTER TABLE direto no banco se necessário para ambiente de desenvolvimento

3. **Verificar a consistência do modelo**
   - Garantir que o modelo `Remessa` no código esteja alinhado com o schema do banco
   - Verificar se há outros campos no modelo que não existem no banco

### Fase 2: Correção dos Problemas de CORS

1. **Revisar a configuração CORS atual**
   - Analisar a implementação no arquivo `app.py`
   - Verificar se todas as origens necessárias estão permitidas
   - Garantir que a configuração esteja correta para a porta 5001

2. **Corrigir o tratamento de requisições OPTIONS**
   - Implementar um handler OPTIONS mais robusto
   - Garantir que não haja redirecionamentos durante requisições preflight
   - Adicionar headers CORS apropriados em todas as respostas

3. **Padronizar a configuração em todos os endpoints**
   - Verificar se há configurações CORS específicas em blueprints individuais
   - Garantir consistência em todas as rotas

### Fase 3: Implementação e Testes

1. **Implementar as correções**
   - Aplicar as alterações no schema do banco
   - Atualizar a configuração CORS
   - Corrigir quaisquer inconsistências no modelo

2. **Testar as correções**
   - Verificar se a coluna `task_id` está presente e funcional
   - Testar todas as rotas que apresentavam erros de CORS
   - Validar a integração frontend-backend

3. **Documentar as mudanças**
   - Atualizar a documentação do projeto
   - Criar instruções para futuros desenvolvedores

## Detalhes de Implementação

### Correção do Schema do Banco

```sql
-- SQL para adicionar a coluna task_id se necessário
ALTER TABLE remessas ADD COLUMN IF NOT EXISTS task_id VARCHAR(50);
```

### Correção da Configuração CORS

```python
# Configuração CORS centralizada e unificada
allowed_origins = [
    "http://localhost:5173", "http://127.0.0.1:5173",  # Frontend Vite dev server
    "http://localhost:5000", "http://127.0.0.1:5000",  # Backend porta padrão
    "http://localhost:5001", "http://127.0.0.1:5001",  # Backend porta alternativa
]

CORS(app, 
     origins=allowed_origins,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Handler OPTIONS robusto para evitar redirecionamentos
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.status_code = 200
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
    return response, 200
```

## Próximos Passos

Após a implementação das correções:

1. Monitorar os logs do backend para identificar quaisquer erros persistentes
2. Verificar o console do navegador para confirmar que os erros de CORS foram resolvidos
3. Validar a funcionalidade completa da aplicação, especialmente nas seções que apresentavam erros
4. Considerar a implementação de testes automatizados para evitar regressões
