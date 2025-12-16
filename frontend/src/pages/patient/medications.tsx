import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { Upload, AlertTriangle, Check } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";

const patientSections = [
  { id: "overview", label: "Overview" },
  { id: "vitals", label: "Vitals Entry" },
  { id: "medications", label: "Medications" },
  { id: "assistant", label: "AI Assistant" },
];

export default function PatientMedications() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();
  const [newMedication, setNewMedication] = useState("");
  const [prescriptionText, setPrescriptionText] = useState("");

  // Get patient data
  const { data: patient } = useQuery({
    queryKey: ["patient-me"],
    queryFn: () => api.getCurrentPatient(),
  });

  // Get prescriptions
  const { data: prescriptions = [], isLoading } = useQuery({
    queryKey: ["prescriptions", patient?.id],
    queryFn: () => api.getPrescriptions(String(patient.id)),
    enabled: !!patient?.id,
  });

  // Upload prescription mutation
  const uploadPrescriptionMutation = useMutation({
    mutationFn: async (data: { ocrText: string }) => {
      return api.uploadPrescription(String(patient.id), data);
    },
    onSuccess: () => {
      toast({
        title: "Prescription processed successfully",
        description: "Your prescription has been analyzed and added to your records.",
      });
      
  queryClient.invalidateQueries({ queryKey: ["prescriptions", patient.id] });
  queryClient.invalidateQueries({ queryKey: ["alerts"] });
      setPrescriptionText("");
    },
    onError: (error) => {
      console.error("Upload prescription error:", error);
      toast({
        title: "Failed to process prescription",
        description: "Please check your input and try again.",
        variant: "destructive",
      });
    },
  });

  // Drug interaction check mutation
  const checkInteractionsMutation = useMutation({
    mutationFn: async (medications: Array<{ name: string; dose: string; frequency: string }>) => {
      return api.checkDrugInteractions(medications);
    },
  });

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "overview" ? "" : section}`);
  };

  const handleUploadPrescription = () => {
    if (!prescriptionText.trim()) {
      toast({
        title: "Please enter prescription text",
        description: "Enter the text from your prescription or upload an image.",
        variant: "destructive",
      });
      return;
    }

    uploadPrescriptionMutation.mutate({ ocrText: prescriptionText });
  };

  const handleCheckInteractions = () => {
    const allMedications: Array<{ name: string; dose: string; frequency: string }> = [];
    
    prescriptions.forEach((prescription: any) => {
      if (prescription.parsedMedications) {
        allMedications.push(...prescription.parsedMedications);
      }
    });

    if (newMedication.trim()) {
      allMedications.push({
        name: newMedication.trim(),
        dose: "Unknown",
        frequency: "Unknown"
      });
    }

    if (allMedications.length === 0) {
      toast({
        title: "No medications to check",
        description: "Add some medications first.",
        variant: "destructive",
      });
      return;
    }

    checkInteractionsMutation.mutate(allMedications);
  };

  const currentMedications = prescriptions
    .flatMap((p: any) => p.parsedMedications || [])
    .filter((med: any) => med.name);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          sections={patientSections}
          onSectionChange={handleSectionChange}
          currentSection="medications"
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
        sections={patientSections}
        onSectionChange={handleSectionChange}
        currentSection="medications"
      />

      <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Medications */}
          <div className="lg:col-span-2">
            <Card className="mb-6" data-testid="card-current-medications">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold text-foreground mb-4">Current Medications</h3>
                {currentMedications.length > 0 ? (
                  <div className="space-y-4">
                    {currentMedications.map((medication: any, index: number) => (
                      <div key={index} className="border border-border rounded-lg p-4" data-testid={`medication-${index}`}>
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-foreground">{medication.name}</h4>
                          <Badge variant="secondary" data-testid={`status-${index}`}>Active</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {medication.dose} {medication.frequency}
                        </p>
                        {medication.instructions && (
                          <p className="text-xs text-muted-foreground mb-2">
                            {medication.instructions}
                          </p>
                        )}
                        <div className="mt-3 flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            data-testid={`button-details-${index}`}
                          >
                            View Details
                          </Button>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            className="text-accent hover:underline"
                            onClick={handleCheckInteractions}
                            data-testid={`button-interactions-${index}`}
                          >
                            Check Interactions
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No medications recorded yet.</p>
                )}
              </CardContent>
            </Card>
            
            {/* Prescription Upload */}
            <Card data-testid="card-prescription-upload">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold text-foreground mb-4">Add New Prescription</h3>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="prescriptionText" className="block text-sm font-medium text-foreground mb-2">
                      Prescription Text
                    </Label>
                    <Textarea
                      id="prescriptionText"
                      value={prescriptionText}
                      onChange={(e) => setPrescriptionText(e.target.value)}
                      placeholder="Enter prescription text here or copy from an image/document..."
                      rows={6}
                      data-testid="textarea-prescription"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Example: "Lisinopril 10mg once daily with food, Metformin 500mg twice daily with meals"
                    </p>
                  </div>
                  
                  <Button
                    onClick={handleUploadPrescription}
                    disabled={uploadPrescriptionMutation.isPending}
                    className="w-full"
                    data-testid="button-upload-prescription"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    {uploadPrescriptionMutation.isPending ? "Processing..." : "Process Prescription"}
                  </Button>
                </div>

                {/* Show analysis from the most recent prescription */}
                {prescriptions.length > 0 && (
                  <div className="mt-6 space-y-3">
                    {prescriptions[0].analysis?.summary && (
                      <div className="p-3 border rounded">
                        <h4 className="font-medium text-foreground">AI Prescription Summary</h4>
                        <p className="text-sm text-muted-foreground mt-1">{prescriptions[0].analysis.summary}</p>
                      </div>
                    )}

                    {prescriptions[0].analysis?.findings?.length > 0 && (
                      <div className="p-3 border rounded">
                        <h4 className="font-medium text-foreground">Findings</h4>
                        <ul className="list-disc ml-5 text-sm text-muted-foreground mt-1">
                          {prescriptions[0].analysis.findings.map((f: any, i: number) => (
                            <li key={i}>{f.message}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {prescriptions[0].flags && prescriptions[0].flags.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-medium text-foreground">Flags</h4>
                        {prescriptions[0].flags.map((flag: any, index: number) => (
                          <Alert key={index} className={`${
                            flag.severity === "high" ? "border-destructive" : 
                            flag.severity === "medium" ? "border-accent" : "border-secondary"
                          }`}>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>{flag.message}</AlertDescription>
                          </Alert>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          
          {/* Drug Interaction Checker */}
          <div>
            <Card className="mb-6" data-testid="card-drug-checker">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">Drug Interaction Checker</h3>
                <div className="space-y-3">
                  <Input
                    value={newMedication}
                    onChange={(e) => setNewMedication(e.target.value)}
                    placeholder="Add medication or supplement..."
                    data-testid="input-new-medication"
                  />
                  <Button
                    onClick={handleCheckInteractions}
                    disabled={checkInteractionsMutation.isPending}
                    className="w-full"
                    data-testid="button-check-interactions"
                  >
                    {checkInteractionsMutation.isPending ? "Checking..." : "Check Interactions"}
                  </Button>
                </div>
                
                {/* Show interaction results */}
                {checkInteractionsMutation.data && (
                  <div className="mt-4 space-y-3">
                    {checkInteractionsMutation.data.interactions.length > 0 ? (
                      checkInteractionsMutation.data.interactions.map((interaction: any, index: number) => (
                        <Alert key={index} className={`${
                          interaction.severity === "major" ? "border-destructive" : 
                          interaction.severity === "moderate" ? "border-accent" : "border-secondary"
                        }`}>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            <p className="font-medium">
                              {interaction.severity === "major" ? "Major" : 
                               interaction.severity === "moderate" ? "Moderate" : "Minor"} Interaction
                            </p>
                            <p className="text-xs mt-1">{interaction.description}</p>
                          </AlertDescription>
                        </Alert>
                      ))
                    ) : (
                      <Alert>
                        <Check className="h-4 w-4" />
                        <AlertDescription>No interactions found.</AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Today's Schedule */}
            <Card data-testid="card-todays-schedule">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">Today's Schedule</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-secondary/10 rounded">
                    <div className="text-sm">
                      <p className="font-medium">8:00 AM</p>
                      <p className="text-xs text-muted-foreground">Lisinopril</p>
                    </div>
                    <Check className="w-5 h-5 text-secondary" />
                  </div>
                  <div className="flex items-center justify-between p-2 bg-muted rounded">
                    <div className="text-sm">
                      <p className="font-medium">8:00 PM</p>
                      <p className="text-xs text-muted-foreground">Metformin</p>
                    </div>
                    <div className="w-5 h-5 border-2 border-muted-foreground rounded"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
