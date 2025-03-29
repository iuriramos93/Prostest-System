import { useState, useEffect } from "react";
import { Wifi, WifiOff } from "lucide-react";

export function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    // Função para atualizar o estado de conexão
    const updateOnlineStatus = () => {
      setIsOnline(navigator.onLine);
    };

    // Adiciona os event listeners
    window.addEventListener("online", updateOnlineStatus);
    window.addEventListener("offline", updateOnlineStatus);

    // Cleanup: remove os event listeners quando o componente é desmontado
    return () => {
      window.removeEventListener("online", updateOnlineStatus);
      window.removeEventListener("offline", updateOnlineStatus);
    };
  }, []);

  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <div 
        className={`h-2.5 w-2.5 rounded-full ${isOnline ? "bg-green-500" : "bg-red-500"}`}
        title={isOnline ? "Online" : "Offline"}
      />
      <span className="text-xs text-muted-foreground sidebar-item-text whitespace-nowrap">
        {isOnline ? "Online" : "Offline"}
      </span>
    </div>
  );
}