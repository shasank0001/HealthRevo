import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Heart, Bell, LogOut } from "lucide-react";

interface NavbarProps {
  title?: string;
  subtitle?: string;
  onSectionChange?: (section: string) => void;
  currentSection?: string;
  sections?: Array<{ id: string; label: string }>;
}

export function Navbar({ 
  title = "HealthRevo", 
  subtitle, 
  onSectionChange, 
  currentSection,
  sections = [] 
}: NavbarProps) {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-card border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center mr-3">
              <Heart className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">{title}</span>
            {subtitle && (
              <span className="ml-2 text-sm bg-secondary text-secondary-foreground px-2 py-1 rounded">
                {subtitle}
              </span>
            )}
          </div>

          {sections.length > 0 && (
            <div className="hidden md:flex items-center space-x-8">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => onSectionChange?.(section.id)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentSection === section.id
                      ? "nav-active"
                      : "text-muted-foreground hover:text-primary"
                  }`}
                  data-testid={`nav-${section.id}`}
                >
                  {section.label}
                </button>
              ))}
            </div>
          )}

          <div className="flex items-center">
            <button 
              className="relative p-2 text-muted-foreground hover:text-foreground transition-colors mr-3"
              data-testid="button-notifications"
            >
              <Bell className="w-6 h-6" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-destructive rounded-full animate-pulse"></span>
            </button>

            <Button
              variant="ghost"
              onClick={logout}
              className="text-muted-foreground hover:text-foreground"
              data-testid="button-logout"
            >
              <span className="text-sm font-medium mr-2">
                {user?.fullName || "User"}
              </span>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
