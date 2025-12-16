import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Navbar } from "@/components/layout/navbar";
import { ChatWidget } from "@/components/ui/chat-widget";
import { useLocation } from "wouter";

const patientSections = [
  { id: "overview", label: "Overview" },
  { id: "vitals", label: "Vitals Entry" },
  { id: "medications", label: "Medications" },
  { id: "assistant", label: "AI Assistant" },
];

export default function PatientAssistant() {
  const { user } = useAuth();
  const [, navigate] = useLocation();

  // Get patient data
  const { data: patient, isLoading } = useQuery({
    queryKey: ["patient", user?.id],
    queryFn: () => api.getCurrentPatient(),
    enabled: !!user,
  });

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "overview" ? "" : section}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          sections={patientSections}
          onSectionChange={handleSectionChange}
          currentSection="assistant"
        />
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          sections={patientSections}
          onSectionChange={handleSectionChange}
          currentSection="assistant"
        />
        <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-muted-foreground">Unable to load patient data. Please try refreshing the page.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        sections={patientSections}
        onSectionChange={handleSectionChange}
        currentSection="assistant"
      />

      <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <ChatWidget patientId={patient.id} />
      </div>
    </div>
  );
}
