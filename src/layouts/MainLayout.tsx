
import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import { Toaster } from "@/components/ui/toaster";
import { useIsMobile } from "@/hooks/use-mobile";

export function MainLayout() {
  const isMobile = useIsMobile();
  
  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
      <Sidebar />
      <main className={`flex-1 overflow-auto ${isMobile ? 'p-4' : 'p-6'}`}>
        {isMobile && <div className="h-12" />} {/* Espaço para o botão do menu móvel */}
        <Outlet />
      </main>
      <Toaster />
    </div>
  );
}
