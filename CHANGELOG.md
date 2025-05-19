# Changelog do Prostest-System

## [1.1.0] - 2025-05-19

### Adicionado
- Implementação de rate limiting com Flask-Limiter para proteção contra ataques de força bruta
- Headers de segurança HTTP (Content-Security-Policy, X-XSS-Protection, etc.)
- Configuração aprimorada do Swagger com suporte a Basic Auth
- Documentação detalhada de todos os endpoints da API
- Plano de refatoração e inovação para desenvolvimento futuro

### Alterado
- Remoção completa de todos os resíduos de JWT do backend e frontend
- Padronização da autenticação Basic Auth em todo o sistema
- Otimização da configuração CORS para melhor compatibilidade entre localhost e 127.0.0.1
- Atualização das dependências do backend para versões mais recentes e seguras
- Simplificação do arquivo app/__init__.py para melhor manutenibilidade

### Corrigido
- Problemas de CORS em rotas específicas, especialmente em requisições OPTIONS
- Inconsistências na autenticação entre frontend e backend
- Tratamento de erros mais robusto e padronizado
- Documentação desatualizada referente à autenticação

## [1.0.0] - 2025-05-17

### Adicionado
- Implementação de paginação em listagens extensas
- Integração de exportação na interface do frontend
- Atualização da documentação com README completo

### Alterado
- Atualização do pipeline CI/CD para simplificar a configuração
- Ajustes na configuração do aplicativo
- Atualização de dependências

### Corrigido
- Configuração de CORS no backend
- Bugs na exportação de dados
- Problemas de integração entre frontend e backend
