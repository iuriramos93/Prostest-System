
import { useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ConnectionStatus } from "@/components/ConnectionStatus";
import { useAuth } from "@/hooks/use-auth";
import {
  LayoutDashboard,
  Upload,
  Search,
  FileText,
  X,
  AlertTriangle,
  BarChart2,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User
} from "lucide-react";

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  to: string;
  minimized: boolean;
}

function NavItem({ icon, label, to, minimized }: NavItemProps) {
  const location = useLocation();
  const isActive = location.pathname === to || 
                  (to !== "/" && location.pathname.startsWith(to)) ||
                  (to === "/consulta-titulos" && location.pathname.startsWith("/titulo/"));

  return (
    <NavLink to={to} className="block">
      <div
        className={cn(
          "flex items-center px-4 py-2 my-1 mx-2 rounded-md transition-colors",
          isActive
            ? "bg-primary text-primary-foreground"
            : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
        )}
      >
        <div className="mr-3">{icon}</div>
        {!minimized && <span>{label}</span>}
      </div>
    </NavLink>
  );
}

export function Sidebar() {
  const [minimized, setMinimized] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const toggleMinimized = () => {
    setMinimized(!minimized);
  };
  
  const handleLogout = () => {
    logout();
    navigate("/auth/login");
  };

  return (
    <div className={cn(
      "h-screen bg-white dark:bg-gray-800 shadow transition-all duration-300",
      minimized ? "w-[80px]" : "w-64"
    )}>
      <div className="h-full flex flex-col">
        <div className="p-4 border-b dark:border-gray-600 flex justify-between items-center">
          {!minimized && <h2 className="text-xl font-bold dark:text-white sidebar-title">SISTEMA DE PROTESTO</h2>}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={toggleMinimized}
            className="text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white"
          >
            {minimized ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </Button>
        </div>
        
        <nav className="flex-1 py-4 overflow-y-auto">
          <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" to="/" minimized={minimized} />
          <NavItem icon={<Upload size={20} />} label="Envio de Documentos" to="/envio-documentos" minimized={minimized} />
          <NavItem icon={<Search size={20} />} label="Consulta de Remessas" to="/consulta-remessas" minimized={minimized} />
          <NavItem icon={<FileText size={20} />} label="Consulta de Títulos" to="/consulta-titulos" minimized={minimized} />
          <NavItem icon={<X size={20} />} label="Desistências" to="/desistencias" minimized={minimized} />
          <NavItem icon={<AlertTriangle size={20} />} label="Análise de Erros" to="/analise-erros" minimized={minimized} />
          <NavItem icon={<BarChart2 size={20} />} label="Relatórios" to="/relatorios" minimized={minimized} />
          <NavItem icon={<Settings size={20} />} label="Configurações" to="/configuracoes" minimized={minimized} />
        </nav>
        
        <div className="mt-auto border-t dark:border-gray-600">
          {user && (
            <div className={cn(
              "flex items-center px-4 py-3 text-gray-600 dark:text-gray-300 border-b dark:border-gray-600",
              minimized ? "justify-center" : "justify-between"
            )}>
              <div className="flex items-center">
                <User size={20} className="mr-2" />
                {!minimized && <span className="text-sm font-medium">{user.name}</span>}
              </div>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handleLogout}
                title="Logout"
                className="text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400"
              >
                <LogOut size={18} />
              </Button>
            </div>
          )}
          <ConnectionStatus />
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}
