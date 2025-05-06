# Unificação do Frontend do Sistema de Protesto

Este documento descreve o processo de unificação das pastas de frontend que foram divididas durante o desenvolvimento.

## Estrutura Anterior

O frontend estava dividido em duas pastas:
- `/src` - Continha componentes, layouts, hooks, etc.
- `/frontend` - Continha configurações e alguns serviços

## Nova Estrutura

Após a unificação, todo o código frontend está na pasta `/frontend-unified` com a seguinte estrutura:

```
frontend-unified/
├── public/             # Arquivos estáticos
├── src/                # Código fonte principal
│   ├── components/     # Componentes reutilizáveis
│   ├── layouts/        # Layouts da aplicação
│   ├── pages/          # Páginas da aplicação
│   ├── hooks/          # React hooks personalizados
│   ├── models/         # Interfaces e tipos
│   ├── services/       # Serviços de API
│   ├── lib/            # Bibliotecas e utilitários
│   ├── routes/         # Configurações de rotas
│   ├── App.tsx         # Componente principal
│   ├── main.tsx        # Ponto de entrada
│   └── index.css       # Estilos globais
├── tsconfig.json       # Configuração TypeScript
├── vite.config.ts      # Configuração do Vite
├── package.json        # Dependências e scripts
└── Dockerfile          # Configuração para Docker
```

## Passos para Migração

1. Mova todos os arquivos de `/src` para a estrutura correspondente em `/frontend-unified/src`
2. Mova os arquivos de configuração de `/frontend` para `/frontend-unified`
3. Ajuste as importações nos arquivos conforme necessário
4. Verifique se não há arquivos duplicados ou conflitantes
5. Atualize o docker-compose.yml para apontar para a nova estrutura

## Execução do Ambiente de Desenvolvimento

Para iniciar o ambiente de desenvolvimento unificado:

```bash
# Construir os containers
docker-compose up -d

# Acessar logs do frontend
docker-compose logs -f frontend
```

## Observações Importantes

- Os aliases de importação foram mantidos usando o prefixo `@`
- As configurações de build foram otimizadas no vite.config.ts
- Os testes foram reorganizados para manter a mesma estrutura de pastas 