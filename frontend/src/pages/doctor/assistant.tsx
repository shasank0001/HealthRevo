import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChatWidget } from "@/components/ui/chat-widget";

const doctorSections = [
  { id: "patients", label: "Patient Overview" },
  { id: "alerts", label: "Alerts & Triage" },
  { id: "prescriptions", label: "Prescription Review" },
  { id: "assistant", label: "AI Assistant" },
];

export default function DoctorAssistant() {
  const { user } = useAuth();
  const [, navigate] = useLocation();
  const [selectedPatientId, setSelectedPatientId] = useState<string>("");

  const { data: patients = [], isLoading } = useQuery({
    queryKey: ["patients"],
    queryFn: () => api.listPatients(),
  });

  useEffect(() => {
    if (!selectedPatientId && patients.length > 0) {
      const first = patients[0];
      setSelectedPatientId(String(first.patientId || first.id));
    }
  }, [patients, selectedPatientId]);

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "patients" ? "" : section}`);
  };

  return (
    <div className="min-h-screen bg-background">
  <Navbar title="HealthRevo" subtitle="Doctor Panel" sections={doctorSections} onSectionChange={handleSectionChange} currentSection="assistant" />

      <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Card>
          <CardContent className="p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-2">Select Patient</label>
              <Select value={selectedPatientId} onValueChange={setSelectedPatientId}>
                <SelectTrigger className="w-80">
                  <SelectValue placeholder={isLoading ? "Loading patients..." : "Choose a patient"} />
                </SelectTrigger>
                <SelectContent>
                  {patients.map((p: any) => (
                    <SelectItem key={String(p.patientId || p.id)} value={String(p.patientId || p.id)}>
                      {p.fullName || p.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedPatientId ? (
              <ChatWidget patientId={selectedPatientId} />
            ) : (
              <div className="text-sm text-muted-foreground">No patient selected.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
