import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface RiskBadgeProps {
  riskType: string;
  score: number;
  drivers?: Record<string, any>;
  icon?: string;
  className?: string;
}

export function RiskBadge({ riskType, score, drivers, icon, className }: RiskBadgeProps) {
  const getSeverityColor = (score: number) => {
    if (score >= 70) return "bg-destructive";
    if (score >= 50) return "bg-accent";
    if (score >= 30) return "bg-accent";
    return "bg-secondary";
  };

  const getSeverityLabel = (score: number) => {
    if (score >= 70) return "High Risk";
    if (score >= 50) return "Moderate Risk";
    if (score >= 30) return "Low-Moderate Risk";
    return "Low Risk";
  };

  const formatRiskType = (type: string) => {
    return type
      .replace(/_/g, " ")
      .split(" ")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatDrivers = (drivers?: Record<string, any>) => {
    if (!drivers) return "General factors";
    return Object.entries(drivers)
      .map(([key, value]) => `${key.replace(/_/g, " ")}: ${value}`)
      .join(", ");
  };

  return (
    <div className={`bg-card p-6 rounded-lg border border-border shadow-sm ${className}`} data-testid={`risk-badge-${riskType}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">
          {formatRiskType(riskType)} Risk
        </h3>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <div className="flex items-center">
        <div className="flex-1">
          <Progress 
            value={score} 
            className="w-full h-2"
            data-testid={`progress-${riskType}`}
          />
          <div 
            className={`h-2 rounded-full ${getSeverityColor(score)}`} 
            style={{ width: `${score}%` }}
          />
        </div>
        <span className="ml-3 text-sm font-medium" data-testid={`score-${riskType}`}>
          {Math.round(score)}%
        </span>
      </div>
      <div className="mt-2 flex items-center justify-between">
        <Badge variant="secondary" data-testid={`severity-${riskType}`}>
          {getSeverityLabel(score)}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground mt-2" data-testid={`drivers-${riskType}`}>
        {formatDrivers(drivers)}
      </p>
    </div>
  );
}
