import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { RiskBadge } from "@/components/ui/risk-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";
import { useLocation } from "wouter";

const patientSections = [
  { id: "overview", label: "Overview" },
  { id: "vitals", label: "Vitals Entry" },
  { id: "medications", label: "Medications" },
  { id: "assistant", label: "AI Assistant" },
];

export default function PatientDashboard() {
  const { user } = useAuth();
  const [, navigate] = useLocation();

  // Get patient data
  const { data: patient } = useQuery({
    queryKey: ["patient-me"],
    queryFn: () => api.getCurrentPatient(),
  });

  // Get risk scores
  const { data: riskScores = [] } = useQuery({
    queryKey: ["risk-scores", patient?.id],
    queryFn: () => api.getRiskScores(String(patient.id)),
    enabled: !!patient?.id,
  });

  // Get recent vitals
  const { data: vitals = [] } = useQuery({
    queryKey: ["vitals", patient?.id],
    queryFn: () => api.getVitals(String(patient.id)),
    enabled: !!patient?.id,
  });

  // Get alerts
  const { data: alerts = [] } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.getAlerts(String(patient?.id)),
    enabled: !!patient?.id,
  });

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "overview" ? "" : section}`);
  };

  const latestVitals = vitals[0];
  const highRiskAlert = alerts.find((alert: any) => 
    alert.severity === "serious" || alert.severity === "urgent"
  );

  const getRiskIcon = (type: string) => {
    switch (type) {
      case "hypertension": return "🫀";
      case "diabetes": return "🩸";
      case "heart_disease": return "❤️";
      default: return "📊";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        sections={patientSections}
        onSectionChange={handleSectionChange}
        currentSection="overview"
      />

      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Alert Banner */}
        {highRiskAlert && (
          <Alert className="mb-6 border-l-4 border-accent" data-testid="alert-banner">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <div>
                <p className="font-medium text-accent-foreground">
                  {highRiskAlert.severity === "urgent" ? "Critical Alert" : "Moderate Risk Alert"}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {highRiskAlert.message}
                </p>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Health Risk Scores */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {riskScores.map((risk: any) => (
            <RiskBadge
              key={risk.riskType}
              riskType={risk.riskType}
              score={parseFloat(risk.score)}
              drivers={risk.drivers}
              icon={getRiskIcon(risk.riskType)}
            />
          ))}
        </div>

        {/* Recent Vitals and Medication Reminders */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card data-testid="card-recent-vitals">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Recent Vitals</h3>
              {latestVitals ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Blood Pressure</span>
                    <span className="text-sm font-medium text-accent" data-testid="text-blood-pressure">
                      {latestVitals.systolic}/{latestVitals.diastolic} mmHg
                    </span>
                  </div>
                  {latestVitals.heartRate && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Heart Rate</span>
                      <span className="text-sm font-medium text-foreground" data-testid="text-heart-rate">
                        {latestVitals.heartRate} bpm
                      </span>
                    </div>
                  )}
                  {latestVitals.bloodGlucose && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Blood Sugar</span>
                      <span className="text-sm font-medium text-secondary" data-testid="text-blood-glucose">
                        {latestVitals.bloodGlucose} mg/dL
                      </span>
                    </div>
                  )}
                  {latestVitals.weight && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Weight</span>
                      <span className="text-sm font-medium text-foreground" data-testid="text-weight">
                        {latestVitals.weight} lbs
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No vitals recorded yet.</p>
              )}
              <Button
                onClick={() => navigate("/vitals")}
                className="mt-4 w-full"
                data-testid="button-enter-vitals"
              >
                Enter Today's Vitals
              </Button>
            </CardContent>
          </Card>

          <Card data-testid="card-medication-reminders">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Medication Reminders</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-secondary/10 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-foreground">Lisinopril 10mg</p>
                    <p className="text-xs text-muted-foreground">Take with morning meal</p>
                  </div>
                  <Button size="sm" variant="secondary" data-testid="button-mark-taken-lisinopril">
                    ✓ Taken
                  </Button>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-foreground">Metformin 500mg</p>
                    <p className="text-xs text-muted-foreground">Due at 8:00 PM</p>
                  </div>
                  <Button size="sm" data-testid="button-mark-taken-metformin">
                    Mark Taken
                  </Button>
                </div>
              </div>
              <Button
                variant="outline"
                onClick={() => navigate("/medications")}
                className="mt-4 w-full"
                data-testid="button-view-medications"
              >
                View All Medications
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
