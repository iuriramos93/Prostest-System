// Implementação de lazy loading e code splitting para rotas do React
import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Componente de loading para exibir durante o carregamento
const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    <span className="ml-3">Carregando...</span>
  </div>
);

// Importação lazy dos componentes de página
// Isso divide o código em chunks separados que são carregados apenas quando necessário
// Modificado para usar a sintaxe que garante a exportação default correta
const Dashboard = React.lazy(() => import('../pages/Dashboard').then(module => ({ default: module.Dashboard })));
const ConsultaTitulos = React.lazy(() => import('../pages/ConsultaTitulos').then(module => ({ default: module.ConsultaTitulos })));
const ConsultaRemessas = React.lazy(() => import('../pages/ConsultaRemessas').then(module => ({ default: module.ConsultaRemessas })));
const Desistencias = React.lazy(() => import('../pages/Desistencias').then(module => ({ default: module.Desistencias })));
const Erros = React.lazy(() => import('../pages/Erros').then(module => ({ default: module.Erros })));
const AnaliseErros = React.lazy(() => import('../pages/AnaliseErros').then(module => ({ default: module.AnaliseErros })));
const Relatorios = React.lazy(() => import('../pages/Relatorios').then(module => ({ default: module.Relatorios })));
const DetalhesTitulo = React.lazy(() => import('../pages/DetalhesTitulo').then(module => ({ default: module.DetalhesTitulo })));
const EnvioDocumentos = React.lazy(() => import('../pages/EnvioDocumentos').then(module => ({ default: module.EnvioDocumentos })));
const Configuracoes = React.lazy(() => import('../pages/Configuracoes').then(module => ({ default: module.Configuracoes })));
const Login = React.lazy(() => import('../pages/auth/Login').then(module => ({ default: module.Login })));
const NotFound = React.lazy(() => import('../pages/NotFound').then(module => ({ default: module.NotFound })));

// Componente de autenticação
const RequireAuth = React.lazy(() => import('../components/RequireAuth'));

/**
 * Componente principal de rotas com lazy loading
 * Benefícios:
 * - Reduz o tamanho do bundle inicial
 * - Carrega componentes apenas quando necessário
 * - Melhora o tempo de carregamento inicial
 */
const LazyRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* Rotas públicas */}
        <Route path="/login" element={<Login />} />
        
        {/* Rotas protegidas */}
        <Route element={<RequireAuth />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/titulos" element={<ConsultaTitulos />} />
          <Route path="/titulos/:id" element={<DetalhesTitulo />} />
          <Route path="/remessas" element={<ConsultaRemessas />} />
          <Route path="/desistencias" element={<Desistencias />} />
          <Route path="/erros" element={<Erros />} />
          <Route path="/analise-erros" element={<AnaliseErros />} />
          <Route path="/relatorios" element={<Relatorios />} />
          <Route path="/documentos" element={<EnvioDocumentos />} />
          <Route path="/configuracoes/*" element={<Configuracoes />} />
        </Route>
        
        {/* Rota de fallback */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </Suspense>
  );
};

export default LazyRoutes;