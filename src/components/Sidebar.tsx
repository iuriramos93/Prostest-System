
import { useState } from "react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, LayoutDashboard, Upload, Search, FileText, X, AlertTriangle, BarChart2, Settings } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  to: string;
  minimized: boolean;
}

const NavItem = ({ icon, label, to, minimized }: NavItemProps) => (
  <NavLink 
    to={to}
    className={({ isActive }) => cn(
      "flex items-center px-4 py-3 text-foreground/70 hover:bg-accent hover:text-foreground transition-colors",
      isActive ? "bg-accent text-foreground font-medium" : ""
    )}
  >
    <div className="mr-2">{icon}</div>
    {!minimized && <span className="sidebar-item-text">{label}</span>}
  </NavLink>
);

export function Sidebar() {
  const [minimized, setMinimized] = useState(false);

  const toggleMinimized = () => {
    setMinimized(!minimized);
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
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}
