# Plano de Correção para Erros de CORS e Integração de Dados

## 1. Análise do Problema

### 1.1 Erros de CORS Identificados
- Erro persistente: "Response to preflight request doesn't pass access control check: Redirect is not allowed for a preflight request"
- Ocorre em múltiplas rotas: `/api/remessas`, `/api/desistencias`, `/api/erros`
- Frontend rodando em `http://localhost:5173`
- Backend sendo acessado em `http://localhost:5001` (porta diferente da configurada)

### 1.2 Problemas de Integração de Dados
- Dados da seção "Consulta de títulos" não estão vindo do banco de dados
- Possível uso de dados simulados ou estáticos no frontend

## 2. Causas Raiz Identificadas

### 2.1 Configuração CORS Incompleta
- A configuração atual no backend só permite origens `http://localhost:5173` e `http://127.0.0.1:5173`
- O backend está rodando na porta 5001, mas a configuração CORS não inclui essa porta
- Redirecionamentos durante requisições OPTIONS (preflight) estão causando falhas de CORS

### 2.2 Inconsistência de Portas
- Frontend configurado para acessar `http://localhost:5000` (valor padrão em api.ts)
- Backend rodando em `http://localhost:5001`
- Variável de ambiente `VITE_API_URL` possivelmente não configurada corretamente

### 2.3 Problemas de Integração
- Possível falta de implementação de endpoints para consulta de títulos
- Possível uso de dados simulados no frontend sem integração real com o backend

## 3. Plano de Correção

### 3.1 Correção da Configuração CORS
1. Atualizar a configuração CORS no backend para incluir todas as portas possíveis (5000, 5001)
2. Garantir que todas as origens possíveis sejam permitidas (localhost e 127.0.0.1 com diferentes portas)
3. Implementar um handler OPTIONS mais robusto que evite redirecionamentos
4. Adicionar headers CORS em todas as respostas, incluindo erros e redirecionamentos

### 3.2 Padronização das Portas e URLs
1. Atualizar o arquivo `.env` do frontend para definir `VITE_API_URL` corretamente
2. Garantir que o backend esteja rodando na porta esperada pelo frontend
3. Atualizar o docker-compose.yml para garantir consistência nas portas expostas

### 3.3 Implementação da Integração de Dados
1. Verificar e implementar endpoints para consulta de títulos no backend
2. Remover dados simulados do frontend
3. Garantir que todas as chamadas de API estejam usando os endpoints corretos

### 3.4 Testes e Validação
1. Testar todas as rotas com requisições OPTIONS para garantir que o preflight está funcionando
2. Verificar se os dados estão sendo carregados corretamente do banco de dados
3. Validar a integração completa entre frontend e backend

## 4. Implementação Detalhada

### 4.1 Atualização do Backend (app.py)
- Expandir a lista de origens permitidas no CORS
- Melhorar o handler OPTIONS para evitar redirecionamentos
- Garantir que todos os handlers de erro incluam headers CORS

### 4.2 Atualização do Frontend (api.ts)
- Garantir que a variável de ambiente VITE_API_URL esteja configurada corretamente
- Adicionar fallback para múltiplas portas se necessário

### 4.3 Configuração do Ambiente
- Atualizar arquivos .env para garantir consistência
- Ajustar docker-compose.yml para expor as portas corretas

### 4.4 Implementação de Endpoints Pendentes
- Implementar ou corrigir endpoints para consulta de títulos
- Garantir que todos os endpoints estejam retornando dados do banco de dados

## 5. Monitoramento e Manutenção
- Adicionar logs detalhados para facilitar a depuração de problemas de CORS
- Implementar testes automatizados para validar a configuração CORS
- Documentar a configuração para referência futura
