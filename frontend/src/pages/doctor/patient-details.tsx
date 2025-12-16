import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

const sections = [
  { id: "patients", label: "Patient Overview" },
  { id: "alerts", label: "Alerts & Triage" },
  { id: "prescriptions", label: "Prescription Review" },
  { id: "assistant", label: "AI Assistant" },
];

export default function PatientDetails() {
  const [, navigate] = useLocation();
  const [patient, setPatient] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const match = window.location.pathname.match(/\/patients\/(\d+)/);
    const id = match ? match[1] : null;
    if (!id) {
      navigate("/");
      return;
    }
  (async () => {
      try {
    const p = await api.getPatient(String(id));
        setPatient(p);
        const a = await api.getAlerts(String(id));
        setAlerts(a);
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "patients" ? "" : section}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          title="HealthRevo"
          subtitle="Doctor Panel"
          sections={sections}
          onSectionChange={handleSectionChange}
          currentSection="patients"
        />
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!patient) return null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar
  title="HealthRevo"
        subtitle="Doctor Panel"
        sections={sections}
        onSectionChange={handleSectionChange}
        currentSection="patients"
      />

      <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">{patient.fullName || patient.email}</h1>
            <p className="text-sm text-muted-foreground">Patient ID: {patient.id}</p>
          </div>
          <Button variant="outline" onClick={() => navigate("/")}>Back to Overview</Button>
        </div>

        <Card>
          <CardContent className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">Email</div>
              <div className="text-foreground">{patient.email}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">DOB</div>
              <div className="text-foreground">{patient.dob || "—"}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Gender</div>
              <div className="text-foreground">{patient.gender || "—"}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Blood Group</div>
              <div className="text-foreground">{patient.bloodGroup || "—"}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Recent Alerts</h2>
            </div>
            <div className="space-y-3">
              {alerts.length === 0 && (
                <div className="text-sm text-muted-foreground">No alerts</div>
              )}
              {alerts.map((a) => (
                <div key={a.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                  <div>
                    <div className="font-medium text-foreground">{a.message}</div>
                    <div className="text-xs text-muted-foreground">{new Date(a.generatedAt).toLocaleString()}</div>
                  </div>
                  <Badge variant={a.severity === 'critical' || a.severity === 'urgent' ? 'destructive' : 'secondary'}>
                    {a.severity}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
