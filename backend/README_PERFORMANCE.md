# Melhorias de Performance no Sistema de Protesto

Este documento descreve as melhorias de performance implementadas no ProtestSystem.

## Otimização de Consultas ao Banco de Dados

### Índices e Paginação

- Adicionados índices nas colunas mais consultadas para melhorar a velocidade das queries
- Implementada paginação em todas as listagens para limitar o volume de dados carregados
- Otimizadas consultas N+1 utilizando joins e carregamento eager do SQLAlchemy

### Exemplo de Implementação

```python
# Antes
def listar_titulos():
    titulos = Titulo.query.all()
    return [titulo.to_dict() for titulo in titulos]

# Depois
def listar_titulos(page=1, per_page=20):
    titulos = Titulo.query.order_by(Titulo.data_entrada.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return {
        'items': [titulo.to_dict() for titulo in titulos.items],
        'total': titulos.total,
        'pages': titulos.pages,
        'page': page
    }
```

### Cache de Dados

- Implementado sistema de cache para dados que mudam com pouca frequência
- Utilizado Redis para armazenar resultados de consultas complexas
- Configurado tempo de expiração adequado para cada tipo de dado

## Minimização de Chamadas de API

### Endpoints Agregados

- Criados endpoints que retornam dados compostos para reduzir múltiplas chamadas
- Implementado debounce em inputs de busca no frontend
- Configurado cache no cliente para resultados de leitura

### Exemplo de Implementação

```javascript
// Antes - Múltiplas chamadas
const fetchDashboardData = async () => {
  const remessas = await remessaService.listarRemessas();
  const titulos = await tituloService.listarTitulos();
  const erros = await erroService.listarErros();
  // Processar dados separadamente
};

// Depois - Endpoint agregado
const fetchDashboardData = async () => {
  const dashboardData = await dashboardService.getDashboardData();
  // Todos os dados já vêm processados e prontos para uso
};
```

## Lazy Loading e Code Splitting

### Carregamento Sob Demanda

- Implementado React.lazy() para carregar componentes apenas quando necessário
- Configurado Suspense para exibir fallback durante o carregamento
- Dividido o código em chunks menores para reduzir o bundle inicial

### Exemplo de Implementação

```jsx
// Implementação de lazy loading para rotas
import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Componentes carregados sob demanda
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const ConsultaTitulos = React.lazy(() => import('./pages/ConsultaTitulos'));
const ConsultaRemessas = React.lazy(() => import('./pages/ConsultaRemessas'));

function AppRoutes() {
  return (
    <Suspense fallback={<div className="loading">Carregando...</div>}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/titulos" element={<ConsultaTitulos />} />
        <Route path="/remessas" element={<ConsultaRemessas />} />
      </Routes>
    </Suspense>
  );
}
```

## Compressão de Ativos

### Gzip/Deflate

- Habilitada compressão gzip para respostas do Flask usando Flask-Compress
- Configurado Vite para emitir arquivos .gz durante o build
- Implementada compressão de imagens para formatos eficientes (WebP)

### Exemplo de Implementação

```python
# Configuração do Flask-Compress
from flask_compress import Compress

def create_app(config_name='development'):
    app = Flask(__name__)
    # ... outras configurações
    
    # Inicializar compressão
    Compress(app)
    
    # ... resto da configuração
    return app
```

## Cache no Cliente

### Headers HTTP

- Configurados headers Cache-Control para recursos estáticos
- Implementada memoização no React com useMemo e useCallback
- Utilizada biblioteca SWR para cache e revalidação de dados

### Exemplo de Implementação

```javascript
// Implementação de cache com SWR
import useSWR from 'swr';

const fetcher = url => fetch(url).then(res => res.json());

function TitulosList() {
  const { data, error } = useSWR('/api/titulos', fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    refreshInterval: 60000 // Revalidar a cada minuto
  });
  
  if (error) return <div>Erro ao carregar dados</div>;
  if (!data) return <div>Carregando...</div>;
  
  return (
    <ul>
      {data.items.map(titulo => (
        <li key={titulo.id}>{titulo.numero_titulo}</li>
      ))}
    </ul>
  );
}
```

## Ferramentas de Análise

### Monitoramento de Performance

- Configurado Lighthouse para análise regular do frontend
- Implementados logs de performance no backend
- Adicionado monitoramento de tempo de resposta das APIs

## Configuração

As configurações de performance podem ser ajustadas no arquivo `.env`:

```
CACHE_TIMEOUT=300  # Tempo de cache em segundos
PAGINATION_PER_PAGE=20  # Itens por página nas listagens
COMPRESS_LEVEL=6  # Nível de compressão gzip (1-9)
COMPRESS_MIN_SIZE=500  # Tamanho mínimo para compressão em bytes
```

## Boas Práticas Implementadas

- Otimização de queries SQL com índices e joins adequados
- Paginação em todas as listagens de dados
- Lazy loading de componentes e rotas
- Compressão de respostas HTTP
- Cache eficiente no cliente e servidor
- Monitoramento contínuo de performance