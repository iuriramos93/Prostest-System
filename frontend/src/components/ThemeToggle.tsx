import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Toggle } from "@/components/ui/toggle";

interface ThemeToggleProps {
  variant?: "sidebar" | "icon";
}

export function ThemeToggle({ variant = "sidebar" }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();

  if (variant === "icon") {
    return (
      <Button
        variant="outline"
        size="icon"
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        className="rounded-full"
      >
        {theme === "dark" ? (
          <Sun className="h-5 w-5" />
        ) : (
          <Moon className="h-5 w-5" />
        )}
        <span className="sr-only">Alternar tema</span>
      </Button>
    );
  }

  return (
    <Toggle
      variant="outline"
      size="sm"
      pressed={theme === "dark"}
      onPressedChange={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="w-full justify-start px-4 py-6"
    >
      {theme === "dark" ? (
        <Sun className="h-5 w-5 mr-2" />
      ) : (
        <Moon className="h-5 w-5 mr-2" />
      )}
      <span className="sidebar-item-text">Tema</span>
    </Toggle>
  );
}