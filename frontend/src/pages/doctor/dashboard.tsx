import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLocation } from "wouter";
import { Users, AlertTriangle, FileText, TrendingUp, GalleryThumbnails } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const doctorSections = [
  { id: "patients", label: "Patient Overview" },
  { id: "alerts", label: "Alerts & Triage" },
  { id: "prescriptions", label: "Prescription Review" },
  { id: "assistant", label: "AI Assistant" },
];

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [, navigate] = useLocation();

  // Get all patients with patientId
  const { data: patients = [], isLoading } = useQuery({
    queryKey: ["patients"],
    queryFn: () => api.listPatients(),
  });

  // Get all alerts
  const { data: alerts = [] } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.getAlerts(),
  });

  // Fetch latest vitals for each patientId
  const { data: latestVitalsByPatient = {} } = useQuery({
    queryKey: ["latest-vitals", patients.map((p: any) => p.patientId || p.id).join(",")],
    queryFn: async () => {
      const entries = await Promise.all(
        (patients as Array<{ id: string; patientId?: string }> ).map(async (p) => {
          const pid = String(p.patientId || p.id);
          try {
            const v = await api.getLatestVitals(pid);
            return [pid, v] as const;
          } catch {
            return [pid, null] as const;
          }
        })
      );
      return Object.fromEntries(entries);
    },
    enabled: patients.length > 0,
  });

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "patients" ? "" : section}`);
  };

  const totalPatients = patients.length;
  const highRiskAlerts = alerts.filter((alert: any) => alert.severity === "urgent" || alert.severity === "serious").length;
  const prescriptionFlags = 8;
  const adherenceRate = 89;

  const displayPatients = (patients as Array<{ id: string; email: string; fullName?: string; patientId?: string }> ).map((p, index) => {
    const pid = String(p.patientId || p.id);
    const v = (latestVitalsByPatient as any)[pid] as any | null;
    const lastVitals = v
      ? `${v.systolic ?? "-"}/${v.diastolic ?? "-"} mmHg${v.heartRate ? `, ${v.heartRate} bpm` : ""}`
      : "—";
    return {
      id: pid,
      name: p.fullName || p.email,
      email: p.email,
      riskLevel: "Moderate Risk",
      lastVitals,
      alertsCount: (alerts as any[]).filter(a => String(a.patientId) === pid).length,
      adherence: 88,
    };
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          title="HealthRevo"
          subtitle="Doctor Panel"
          sections={doctorSections}
          onSectionChange={handleSectionChange}
          currentSection="patients"
        />
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar
  title="HealthRevo"
        subtitle="Doctor Panel"
        sections={doctorSections}
        onSectionChange={handleSectionChange}
        currentSection="patients"
      />

      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card data-testid="card-total-patients">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Users className="w-6 h-6 text-primary" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-total-patients">
                    {totalPatients}
                  </p>
                  <p className="text-sm text-muted-foreground">Total Patients</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card data-testid="card-high-risk-alerts">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-destructive/10 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-destructive" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-high-risk-alerts">
                    {highRiskAlerts}
                  </p>
                  <p className="text-sm text-muted-foreground">High Risk Alerts</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card data-testid="card-prescription-flags">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-accent/10 rounded-lg">
                  <FileText className="w-6 h-6 text-accent" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-prescription-flags">
                    {prescriptionFlags}
                  </p>
                  <p className="text-sm text-muted-foreground">Prescription Flags</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card data-testid="card-adherence-rate">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-secondary/10 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-secondary" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-adherence-rate">
                    {adherenceRate}%
                  </p>
                  <p className="text-sm text-muted-foreground">Adherence Rate</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Patient List with Filters */}
        <Card data-testid="card-patient-list">
          <CardContent className="p-6">
            <div className="border-b border-border pb-6 mb-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
                <h2 className="text-xl font-semibold text-foreground">Patient Overview</h2>
                <div className="flex space-x-2">
                  <Select>
                    <SelectTrigger className="w-40" data-testid="select-patient-filter">
                      <SelectValue placeholder="All Patients" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Patients</SelectItem>
                      <SelectItem value="high-risk">High Risk Only</SelectItem>
                      <SelectItem value="alerts">Recent Alerts</SelectItem>
                      <SelectItem value="overdue">Overdue Vitals</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Search patients..."
                    className="w-64"
                    data-testid="input-search-patients"
                  />
                </div>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="table-patients">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Patient</th>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Risk Level</th>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Last Vitals</th>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Alerts</th>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Adherence</th>
                    <th className="text-left py-3 px-6 text-sm font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {displayPatients.map((patient, index) => (
                    <tr key={patient.id} className="hover:bg-muted/50 transition-colors" data-testid={`row-patient-${index}`}>
                      <td className="py-4 px-6">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center mr-3">
                            <span className="text-sm font-medium text-primary-foreground">
                              {patient.name.split(" ").map((n: string) => n[0]).join("")}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-foreground" data-testid={`text-patient-name-${index}`}>
                              {patient.name}
                            </p>
                            <p className="text-sm text-muted-foreground">{patient.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <Badge
                          variant={
                            patient.riskLevel === "High Risk" ? "destructive" :
                            patient.riskLevel === "Moderate Risk" ? "secondary" : "outline"
                          }
                          data-testid={`badge-risk-${index}`}
                        >
                          {patient.riskLevel}
                        </Badge>
                      </td>
                      <td className="py-4 px-6 text-sm text-muted-foreground" data-testid={`text-last-vitals-${index}`}>
                        {patient.lastVitals}
                      </td>
                      <td className="py-4 px-6">
                        {patient.alertsCount > 0 ? (
                          <Badge variant="destructive" data-testid={`badge-alert-${index}`}>
                            {patient.alertsCount} alert{patient.alertsCount > 1 ? "s" : ""}
                          </Badge>
                        ) : (
                          <span className="text-sm text-muted-foreground">None</span>
                        )}
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center">
                          <div className="w-16 bg-muted rounded-full h-2 mr-2">
                            <Progress value={patient.adherence} className="h-2" />
                          </div>
                          <span className="text-sm text-muted-foreground" data-testid={`text-adherence-${index}`}>
                            {patient.adherence}%
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-primary hover:text-primary/80"
                          data-testid={`button-view-details-${index}`}
                          onClick={() => navigate(`/patients/${patient.id}`)}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
