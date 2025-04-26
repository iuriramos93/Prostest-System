# Melhorias de Segurança no Sistema de Autenticação

Este documento descreve as melhorias de segurança implementadas no sistema de autenticação do ProtestSystem.

## Armazenamento Seguro de Credenciais

### Variáveis de Ambiente

As credenciais sensíveis agora são armazenadas em variáveis de ambiente através de um arquivo `.env`. Um arquivo de exemplo `.env.example` foi criado com as configurações necessárias.

Para configurar o ambiente:

1. Copie o arquivo `.env.example` para `.env`
2. Preencha com valores reais e seguros
3. O arquivo `.env` já está incluído no `.gitignore` para evitar que seja commitado acidentalmente

### Hash de Senhas com Bcrypt

As senhas de usuários agora são armazenadas usando hash seguro com bcrypt, em vez de texto puro. O modelo `User` foi atualizado para usar o Flask-Bcrypt.

### Migração de Senhas Existentes

Para migrar as senhas existentes para o formato bcrypt, execute o script de migração:

```bash
python migrate_passwords.py
```

Este script converte automaticamente todas as senhas em texto puro para hash bcrypt seguro.

## Otimização da Autenticação

### Autenticação com JWT

O sistema agora utiliza JWT (JSON Web Tokens) com as seguintes melhorias:

- Tokens de acesso de curta duração (24 horas por padrão)
- Refresh tokens de longa duração (7 dias por padrão)
- Armazenamento de tokens em cookies HttpOnly e Secure
- Proteção contra CSRF

### Cache de Dados de Usuário

Implementamos um sistema de cache para dados de usuário que:

- Reduz consultas ao banco de dados
- Armazena dados de usuário em memória por 5 minutos
- Limpa automaticamente o cache quando informações do usuário são atualizadas

### Novas Rotas de Autenticação

- `/auth/refresh` - Para renovar tokens de acesso usando refresh tokens
- `/auth/logout` - Para encerrar sessão e invalidar tokens

## Configuração de Segurança

As configurações de segurança podem ser ajustadas no arquivo `.env`:

```
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 horas em segundos
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 dias em segundos
JWT_COOKIE_SECURE=true  # Ative em produção
```

## Boas Práticas Implementadas

- Cookies com flags HttpOnly e Secure
- Proteção contra XSS
- Separação de configurações por ambiente
- Validação de tokens eficiente
- Minimização de overhead no login