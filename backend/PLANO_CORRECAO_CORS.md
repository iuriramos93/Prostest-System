# Plano de Implementação para Correção de Erros CORS

## Diagnóstico do Problema

Após análise dos erros apresentados no console do navegador, identificamos problemas de configuração CORS (Cross-Origin Resource Sharing) no backend Flask que estão impedindo a comunicação adequada entre o frontend (porta 5173) e o backend (porta 5001).

Os principais erros identificados foram:

1. **Cabeçalho `authorization` não permitido nas requisições preflight**
   ```
   Access to XMLHttpRequest at 'http://localhost:5001/api/relatorios?tipo=dashboard' from origin 'http://localhost:5173' has been blocked by CORS policy: Request header field authorization is not allowed by Access-Control-Allow-Headers in preflight response.
   ```

2. **Redirecionamentos não permitidos em requisições preflight**
   ```
   Access to XMLHttpRequest at 'http://localhost:5001/api/remessas?page=1&per_page=10' from origin 'http://localhost:5173' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: Redirect is not allowed for a preflight request.
   ```

3. **Falha na comunicação entre frontend e backend**
   ```
   Erro ao listar relatórios: AxiosError {message: 'Network Error', name: 'AxiosError', code: 'ERR_NETWORK', ...}
   ```

## Solução Implementada

### 1. Criação de Configuração CORS Centralizada

Criamos um módulo específico para configuração CORS em `config/cors.py` que implementa:

- Lista centralizada de origens permitidas
- Configuração de cabeçalhos permitidos, incluindo `Authorization`
- Configuração de métodos HTTP permitidos
- Configuração de credenciais permitidas
- Configuração de cache para requisições preflight

### 2. Implementação de Middleware WSGI

Implementamos dois middlewares WSGI em `app/utils/middleware.py`:

- **PreflightMiddleware**: Intercepta requisições OPTIONS e responde diretamente sem passar pelo Flask, evitando redirecionamentos
- **CORSHeadersMiddleware**: Garante que todas as respostas tenham os headers CORS corretos, mesmo em caso de erro

### 3. Atualização da Aplicação Flask

Modificamos os arquivos principais da aplicação:

- **app/__init__.py**: Removemos a configuração CORS embutida e usamos a configuração centralizada
- **app.py**: Atualizamos para usar a nova configuração CORS e os middlewares

### 4. Correção do Middleware de Autenticação

Corrigimos o middleware de autenticação em `app/auth/middleware.py` para usar o método correto de verificação de senha (`verify_password` em vez de `check_password`).

## Instruções de Implementação

1. **Copiar os novos arquivos**:
   - `config/cors.py`
   - `app/utils/middleware.py`

2. **Atualizar os arquivos existentes**:
   - `app/__init__.py`
   - `app.py`
   - `app/auth/middleware.py`

3. **Reiniciar o servidor Flask**:
   ```bash
   # Parar o servidor atual
   # Iniciar o servidor com as novas configurações
   python run_server.py
   ```

4. **Verificar a configuração CORS**:
   ```bash
   python scripts/test_cors_simple.py
   ```

## Verificação da Solução

Para verificar se a solução foi implementada corretamente, execute o script de teste CORS e verifique se:

1. Todas as requisições OPTIONS retornam status 200
2. Todas as respostas incluem os headers CORS corretos:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Methods`
   - `Access-Control-Allow-Headers` (incluindo `Authorization`)
   - `Access-Control-Allow-Credentials`

3. O frontend consegue se comunicar com o backend sem erros CORS

## Considerações Adicionais

- Esta solução mantém a segurança da API, permitindo apenas origens específicas
- O cache de preflight (3600 segundos) reduz o número de requisições OPTIONS
- Os middlewares WSGI garantem que todas as respostas tenham os headers CORS corretos, mesmo em caso de erro
- A configuração centralizada facilita a manutenção e atualização das políticas CORS 