
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { AuthProvider } from "@/hooks/use-auth";
import { RequireAuth } from "@/components/RequireAuth";

import { MainLayout } from "@/layouts/MainLayout";
import { Dashboard } from "@/pages/Dashboard";
import { EnvioDocumentos } from "@/pages/EnvioDocumentos";
import { ConsultaRemessas } from "@/pages/ConsultaRemessas";
import { ConsultaTitulos } from "@/pages/ConsultaTitulos";
import { Login } from "@/pages/auth/Login";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Rota pública de autenticação */}
            <Route path="/login" element={<Login />} />
            
            {/* Rotas protegidas */}
            <Route element={<RequireAuth><MainLayout /></RequireAuth>}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/envio-documentos" element={<EnvioDocumentos />} />
              <Route path="/consulta-remessas" element={<ConsultaRemessas />} />
              <Route path="/consulta-titulos" element={<ConsultaTitulos />} />
              {/* Outras rotas protegidas seriam adicionadas aqui */}
            </Route>
            
            {/* Rota de fallback */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
