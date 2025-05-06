# ProtestSystem

Sistema de Gestão de Protestos desenvolvido com React e Flask.

## Estrutura do Projeto

Após a unificação das pastas de frontend, o projeto possui a seguinte estrutura:

```
/
├── backend/            # Código do backend em Flask
├── src/                # Código do frontend em React
│   ├── components/     # Componentes reutilizáveis
│   ├── hooks/          # Custom hooks React
│   ├── layouts/        # Layouts da aplicação
│   ├── lib/            # Bibliotecas e utilitários
│   ├── models/         # Interfaces e tipos
│   ├── pages/          # Páginas da aplicação
│   ├── routes/         # Configuração de rotas
│   ├── services/       # Serviços para API
│   ├── App.tsx         # Componente principal
│   ├── main.tsx        # Entrada da aplicação
│   └── ...
├── docker-compose.yml  # Configuração do Docker Compose
├── Dockerfile          # Configuração do Docker para o frontend
├── package.json        # Dependências do projeto
└── vite.config.ts      # Configuração do Vite
```

## Requisitos

- Node.js 18+
- Docker e Docker Compose

## Executando o Projeto

1. Instale as dependências:
```
npm install
```

2. Execute a aplicação com Docker Compose:
```
docker-compose up -d
```

3. Acesse a aplicação:
   - Frontend: http://localhost:3000
   - API: http://localhost:5000
   - PGAdmin: http://localhost:5050

## Desenvolvimento

Para desenvolvimento local sem Docker:

```
npm run dev
```

## Testes

Para executar os testes:

```
npm test
```