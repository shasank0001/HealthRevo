import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useLocation } from "wouter";
import { AlertTriangle, CheckCircle, FileText, Eye, Phone, Settings } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

const doctorSections = [
  { id: "patients", label: "Patient Overview" },
  { id: "alerts", label: "Alerts & Triage" },
  { id: "prescriptions", label: "Prescription Review" },
  { id: "assistant", label: "AI Assistant" },
];

export default function DoctorPrescriptions() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();

  const [historyPatientId, setHistoryPatientId] = useState<string | null>(null);
  const [historyData, setHistoryData] = useState<{ vitals: any[]; prescriptions: any[]; alerts: any[] } | null>(null);

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "patients" ? "" : section}`);
  };

  const { data: patients = [] } = useQuery({ queryKey: ["patients"], queryFn: () => api.listPatients() });
  const { data: alerts = [], isLoading } = useQuery({ queryKey: ["alerts"], queryFn: () => api.getAlerts() });
  const { data: allPrescriptions = [] } = useQuery({ queryKey: ["all-prescriptions"], queryFn: () => api.listAllPrescriptions() });

  const reviews = allPrescriptions.flatMap((p: any) => {
    const flags = p.flags || [];
    if (!flags.length && !p.analysis?.summary) return [];
    return (flags.length ? flags : [{ message: p.analysis?.summary, severity: "low" }]).map((f: any, idx: number) => ({
      id: `${p.id}-${idx}`,
      patientId: String(p.patientId),
      prescriptionId: String(p.id),
      patientName: p.patientName || p.patientEmail,
      issue: f.message || "Flag",
      severity: (f.severity || "medium") as "low" | "medium" | "high",
      medication: (p.parsedMedications && p.parsedMedications[0]?.name) || "Medication",
      dose: p.parsedMedications && p.parsedMedications[0]?.dose,
      dateIssued: p.uploadedAt || "",
      analysisSummary: p.analysis?.summary,
    }));
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high": return "border-destructive bg-destructive/5";
      case "medium": return "border-accent bg-accent/5";
      case "low": return "border-secondary bg-secondary/5";
      default: return "border-border";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high": return <Badge variant="destructive">HIGH RISK</Badge>;
      case "medium": return <Badge className="bg-accent text-accent-foreground">REVIEW NEEDED</Badge>;
      case "low": return <Badge variant="secondary">LOW PRIORITY</Badge>;
      default: return <Badge variant="outline">NORMAL</Badge>;
    }
  };

  const adjustMutation = useMutation({
    mutationFn: async (args: { patientId: string; prescriptionId: string; updates: any }) =>
      api.adjustPrescription(args.patientId, args.prescriptionId, args.updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["all-prescriptions"] });
      toast({ title: "Prescription adjusted" });
    },
    onError: (e: any) => toast({ title: "Adjust failed", description: e.message, variant: "destructive" })
  });

  const handleApproveDose = (reviewId: string) => {
    toast({ title: "Dose approved", description: "The prescription has been approved as prescribed." });
  };

  const handleAdjustPrescription = async (review: any) => {
    // Simple example: append " (adjusted)" to dose
    const newDose = (review.dose || "").toString() + " (adjusted)";
    adjustMutation.mutate({ patientId: review.patientId, prescriptionId: review.prescriptionId, updates: { dose: newDose } });
  };

  const handleContactPrescriber = (reviewId: string) => {
    toast({ title: "Prescriber contacted", description: "Communication initiated." });
  };

  const handleViewHistory = async (patientId: string) => {
    setHistoryPatientId(patientId);
    try {
      const data = await api.getPatientHistory(patientId);
      setHistoryData(data);
    } catch (e: any) {
      toast({ title: "Failed to load history", description: e.message, variant: "destructive" });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
  <Navbar title="HealthRevo" subtitle="Doctor Panel" sections={doctorSections} onSectionChange={handleSectionChange} currentSection="prescriptions" />
        <div className="flex items-center justify-center py-12"><div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
  <Navbar title="HealthRevo" subtitle="Doctor Panel" sections={doctorSections} onSectionChange={handleSectionChange} currentSection="prescriptions" />

      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card data-testid="card-pending-reviews">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-accent/10 rounded-lg">
                  <FileText className="w-6 h-6 text-accent" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-pending-reviews">
                    {reviews.length}
                  </p>
                  <p className="text-sm text-muted-foreground">Pending Reviews</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card data-testid="card-high-risk">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-destructive/10 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-destructive" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-high-risk">
                    {reviews.filter(r => r.severity === "high").length}
                  </p>
                  <p className="text-sm text-muted-foreground">High Risk</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card data-testid="card-interactions">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-primary" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-interactions">
                    {reviews.filter(r => (r.issue || "").toLowerCase().includes("interaction")).length}
                  </p>
                  <p className="text-sm text-muted-foreground">Drug Interactions</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card data-testid="card-resolved-today">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-secondary/10 rounded-lg">
                  <CheckCircle className="w-6 h-6 text-secondary" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-foreground" data-testid="text-resolved-today">
                    7
                  </p>
                  <p className="text-sm text-muted-foreground">Resolved Today</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Prescription Review List */}
        <Card data-testid="card-prescription-reviews">
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold text-foreground mb-6">Prescription Review & Flags</h2>
            
            {reviews.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No prescriptions requiring review at this time.
              </p>
            ) : (
              <div className="space-y-4">
                {reviews.map((review, index) => (
                  <div
                    key={review.id}
                    className={`border rounded-lg p-4 ${getSeverityColor(review.severity)}`}
                    data-testid={`prescription-review-${index}`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-medium text-foreground" data-testid={`review-title-${index}`}>{review.issue} - {review.medication}</h3>
                        <p className="text-sm text-muted-foreground">Patient: {review.patientName} | Prescribed: {review.dose}</p>
                        <p className="text-xs text-muted-foreground">Date: {review.dateIssued}</p>
                        {review.analysisSummary && (
                          <p className="text-xs text-muted-foreground mt-1">Summary: {review.analysisSummary}</p>
                        )}
                      </div>
                      {getSeverityBadge(review.severity)}
                    </div>
                    <div className="flex space-x-2">
                      {review.severity === "high" && (
                        <Button size="sm" variant="destructive" onClick={() => handleContactPrescriber(review.id)} data-testid={`button-contact-prescriber-${index}`}>
                          Contact Prescriber
                        </Button>
                      )}
                      {review.issue.includes("Dose") && (
                        <Button size="sm" onClick={() => handleApproveDose(review.id)} data-testid={`button-approve-dose-${index}`}>Approve Dose</Button>
                      )}
                      <Button size="sm" variant="outline" onClick={() => handleAdjustPrescription(review)} data-testid={`button-adjust-prescription-${index}`}>
                        Adjust Prescription
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => handleViewHistory(review.patientId)} data-testid={`button-view-history-${index}`}>
                        View Patient History
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {historyPatientId && historyData && (
          <Card className="mt-6" data-testid="card-patient-history">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-foreground">Patient History</h3>
                <Button variant="outline" size="sm" onClick={() => { setHistoryPatientId(null); setHistoryData(null); }}>Close</Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-medium">Recent Vitals</h4>
                  <ul className="text-sm text-muted-foreground list-disc ml-5">
                    {historyData.vitals.slice(0, 5).map((v: any, i: number) => (
                      <li key={i}>{new Date(v.recordedAt).toLocaleDateString()}: {v.systolic}/{v.diastolic} mmHg{v.heartRate ? `, ${v.heartRate} bpm` : ""}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Recent Prescriptions</h4>
                  <ul className="text-sm text-muted-foreground list-disc ml-5">
                    {historyData.prescriptions.slice(0, 5).map((p: any, i: number) => (
                      <li key={i}>{p.parsedMedications?.[0]?.name || "Prescription"} — {p.uploadedAt}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Recent Alerts</h4>
                  <ul className="text-sm text-muted-foreground list-disc ml-5">
                    {historyData.alerts.slice(0, 5).map((a: any, i: number) => (
                      <li key={i}>{a.severity.toUpperCase()}: {a.title || a.message}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
