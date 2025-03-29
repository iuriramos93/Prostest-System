
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainLayout } from "@/layouts/MainLayout";
import { Dashboard } from "@/pages/Dashboard";
import { EnvioDocumentos } from "@/pages/EnvioDocumentos";
import { ConsultaRemessas } from "@/pages/ConsultaRemessas";
import { ConsultaTitulos } from "@/pages/ConsultaTitulos";
import { Desistencias } from "@/pages/Desistencias";
import { AnaliseErros } from "@/pages/AnaliseErros";
import { Relatorios } from "@/pages/Relatorios";
import { DetalhesTitulo } from "./pages/DetalhesTitulo";
import { Configuracoes } from "@/pages/Configuracoes";
import NotFound from "@/pages/NotFound";
import { Login } from "@/pages/auth/Login";
import { RequireAuth } from "@/components/RequireAuth";
import { ThemeProvider } from "@/hooks/use-theme";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/hooks/use-auth";

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="titletrack-theme">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route element={<RequireAuth />}>
              <Route element={<MainLayout />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/envio-documentos" element={<EnvioDocumentos />} />
                <Route path="/consulta-remessas" element={<ConsultaRemessas />} />
                <Route path="/consulta-titulos" element={<ConsultaTitulos />} />
                <Route path="/titulo/:id" element={<DetalhesTitulo />} />
                <Route path="/desistencias" element={<Desistencias />} />
                <Route path="/analise-erros" element={<AnaliseErros />} />
                <Route path="/relatorios" element={<Relatorios />} />
                <Route path="/configuracoes" element={<Configuracoes />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
