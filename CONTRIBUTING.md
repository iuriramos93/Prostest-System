# Guia de Contribuição para o Sistema de Protesto

Obrigado por considerar contribuir para o Sistema de Protesto! Este documento fornece diretrizes e instruções para ajudar novos desenvolvedores a contribuir com o projeto.

## Índice

1. [Configuração do Ambiente](#configuração-do-ambiente)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Fluxo de Trabalho de Desenvolvimento](#fluxo-de-trabalho-de-desenvolvimento)
4. [Padrões de Código](#padrões-de-código)
5. [Testes](#testes)
6. [Documentação](#documentação)
7. [Processo de Pull Request](#processo-de-pull-request)

## Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- Node.js 18+
- Docker e Docker Compose
- PostgreSQL 13+

### Passos para Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/ProtestSystem.git
   cd ProtestSystem
   ```

2. Configure o ambiente backend:
   ```bash
   cd backend
   cp .env.example .env  # Edite o arquivo .env com suas configurações
   pip install -r requirements.txt
   ```

3. Configure o ambiente frontend:
   ```bash
   cd ..
   npm install
   ```

4. Inicie o ambiente de desenvolvimento com Docker:
   ```bash
   docker-compose up -d
   ```

## Estrutura do Projeto

### Backend (Flask)

```
backend/
├── app/                  # Código principal da aplicação
│   ├── auth/             # Módulo de autenticação
│   ├── protestos/        # Módulo de protestos
│   ├── titulos/          # Módulo de títulos
│   └── ...               # Outros módulos
├── tests/                # Testes automatizados
├── migrations/           # Migrações de banco de dados
└── app.py                # Ponto de entrada da aplicação
```

### Frontend (React + Vite)

```
src/
├── components/           # Componentes reutilizáveis
├── hooks/                # React hooks personalizados
├── pages/                # Páginas da aplicação
├── services/             # Serviços de API
└── utils/                # Utilitários
```

## Fluxo de Trabalho de Desenvolvimento

1. **Crie uma branch para sua feature ou correção**:
   ```bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/nome-do-bug
   ```

2. **Desenvolva e teste suas alterações localmente**

3. **Escreva testes para suas alterações**

4. **Atualize a documentação conforme necessário**

5. **Envie suas alterações**:
   ```bash
   git add .
   git commit -m "Descrição clara das alterações"
   git push origin feature/nome-da-feature
   ```

6. **Crie um Pull Request**

## Padrões de Código

### Python (Backend)

- Siga o PEP 8 para estilo de código
- Use docstrings para documentar funções e classes
- Organize imports em ordem alfabética
- Use tipagem estática quando possível

### JavaScript/TypeScript (Frontend)

- Siga o estilo ESLint configurado no projeto
- Use componentes funcionais e hooks do React
- Prefira funções assíncronas com async/await em vez de Promises encadeadas
- Utilize TypeScript para tipagem estática

## Testes

### Backend

- Escreva testes unitários e de integração usando pytest
- Execute os testes antes de enviar um PR:
  ```bash
  cd backend
  python -m pytest
  ```

### Frontend

- Escreva testes de componentes usando Jest e React Testing Library
- Execute os testes antes de enviar um PR:
  ```bash
  npm test
  ```

## Documentação

- Documente novas APIs usando o formato Swagger/OpenAPI
- Atualize o README.md quando adicionar novas funcionalidades
- Mantenha os arquivos de documentação específicos atualizados (README_PERFORMANCE.md, README_SEGURANCA.md)

## Processo de Pull Request

1. Preencha o template de PR com todas as informações necessárias
2. Certifique-se de que todos os testes estão passando
3. Solicite revisão de pelo menos um outro desenvolvedor
4. Responda a quaisquer comentários ou solicitações de alteração
5. Após aprovação, seu PR será mesclado à branch principal

## CI/CD

O projeto utiliza GitHub Actions para CI/CD. Cada push ou PR para as branches `main` ou `develop` acionará:

- Execução de testes automatizados
- Verificação de linting
- Análise de qualidade de código com SonarQube
- Build e push de imagens Docker (apenas para a branch `main`)

---

Se você tiver dúvidas ou precisar de ajuda, não hesite em abrir uma issue ou entrar em contato com a equipe de desenvolvimento.