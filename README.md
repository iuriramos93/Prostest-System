
# Sistema de Protesto - Dashboard

## Visão Geral

Um sistema de dashboard para cartório de protesto, desenvolvido com React, TypeScript e componentes UI modernos. Este sistema permite gerenciar o processo de envio, consulta e análise de remessas e títulos de protesto.

## Tecnologias

### Frontend
- React + Vite (TypeScript)
- Tailwind CSS para estilização
- shadcn/ui para componentes
- TanStack Query para gerenciamento de estado e requisições
- React Router para navegação

### Backend (Preparado para)
- Python 3.11 + Django + Django REST Framework
- Autenticação JWT
- Docker + PostgreSQL

## Funcionalidades Atuais

1. **Autenticação**
   - Sistema de login/logout
   - Proteção de rotas

2. **Dashboard**
   - Visão geral com métricas principais
   - Listagem das últimas remessas

3. **Envio de Documentos**
   - Upload de arquivos XML
   - Seleção de UF e tipo de documento

4. **Consulta de Remessas**
   - Filtros por número, data e status
   - Visualização detalhada

5. **Consulta de Títulos**
   - Busca de títulos por número e data
   - Detalhes completos do título

6. **Tema Claro/Escuro**
   - Suporte para alternância entre temas

## Configuração do Ambiente de Desenvolvimento

```sh
# Clonar o repositório
git clone <URL_DO_REPOSITÓRIO>

# Entrar no diretório do projeto
cd sistema-protesto

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

## Autenticação (Modo de Desenvolvimento)

Para testar a autenticação, use as seguintes credenciais:

- Email: admin@example.com
- Senha: admin123

## Próximos Passos

- Implementação das páginas de Desistências, Análise de Erros e Relatórios
- Integração com backend Django para autenticação e operações CRUD
- Implementação da paginação nas listagens
- Melhorias na responsividade para dispositivos móveis
- Implementação de testes automatizados
