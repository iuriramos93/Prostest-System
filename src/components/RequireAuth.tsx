
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";

export function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Exibir um indicador de carregamento enquanto verifica a autenticação
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirecionar para a página de login, mas manter a URL de origem
    // para redirecionar de volta após o login bem-sucedido
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
