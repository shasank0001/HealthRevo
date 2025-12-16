import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import { Navbar } from "@/components/layout/navbar";
import { VitalsChart } from "@/components/ui/vitals-chart";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const patientSections = [
  { id: "overview", label: "Overview" },
  { id: "vitals", label: "Vitals Entry" },
  { id: "medications", label: "Medications" },
  { id: "assistant", label: "AI Assistant" },
];

const vitalsSchema = z.object({
  systolic: z.number().min(70).max(250).optional(),
  diastolic: z.number().min(40).max(150).optional(),
  heartRate: z.number().min(30).max(200).optional(),
  bloodGlucose: z.number().min(50).max(500).optional(),
  weight: z.number().min(50).max(500).optional(),
  temperature: z.number().min(95).max(110).optional(),
  notes: z.string().optional(),
});

type VitalsFormData = z.infer<typeof vitalsSchema>;

export default function PatientVitals() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();

  const { register, handleSubmit, formState: { errors }, reset } = useForm<VitalsFormData>({
    resolver: zodResolver(vitalsSchema),
  });

  // Fetch the current patient profile to get the correct patient.id
  const { data: patient } = useQuery({
    queryKey: ["patient-me"],
    queryFn: () => api.getCurrentPatient(),
    enabled: !!user,
  });

  // Get vitals history
  const { data: vitalsHistory = [], isLoading } = useQuery({
    queryKey: ["vitals", patient?.id],
    queryFn: () => api.getVitals(String(patient.id)),
    enabled: !!patient?.id,
  });

  // Submit vitals mutation
  const addVitalsMutation = useMutation({
    mutationFn: (vitalsData: any) => api.addVitals(String(patient?.id || ""), vitalsData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vitals", patient?.id] });
      toast({ title: "Vitals added successfully" });
      reset();
    },
    onError: (error: any) => {
      toast({
        title: "Error adding vitals",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "overview" ? "" : section}`);
  };

  const onSubmit = (data: VitalsFormData) => {
    // Filter out undefined values and convert strings to numbers
    const cleanedData = Object.entries(data).reduce((acc, [key, value]) => {
      if (value !== undefined && value !== "" && value !== null) {
        if (key === "notes") {
          acc[key] = value as string;
        } else {
          acc[key] = typeof value === "string" ? parseFloat(value) : value;
        }
      }
      return acc;
    }, {} as any);

    addVitalsMutation.mutate(cleanedData);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          sections={patientSections}
          onSectionChange={handleSectionChange}
          currentSection="vitals"
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
        currentSection="vitals"
      />

      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Vitals Entry Form */}
          <Card data-testid="card-vitals-form">
            <CardContent className="p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6">Daily Vitals Entry</h2>
              
              <form onSubmit={handleSubmit(onSubmit)} data-testid="form-vitals">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="systolic" className="block text-sm font-medium text-foreground mb-2">
                      Blood Pressure (Systolic)
                    </Label>
                    <Input
                      id="systolic"
                      type="number"
                      {...register("systolic", { valueAsNumber: true })}
                      placeholder="120"
                      data-testid="input-systolic"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Normal: 90-120 mmHg</p>
                    {errors.systolic && (
                      <p className="text-sm text-destructive mt-1">{errors.systolic.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="diastolic" className="block text-sm font-medium text-foreground mb-2">
                      Blood Pressure (Diastolic)
                    </Label>
                    <Input
                      id="diastolic"
                      type="number"
                      {...register("diastolic", { valueAsNumber: true })}
                      placeholder="80"
                      data-testid="input-diastolic"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Normal: 60-80 mmHg</p>
                    {errors.diastolic && (
                      <p className="text-sm text-destructive mt-1">{errors.diastolic.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="heartRate" className="block text-sm font-medium text-foreground mb-2">
                      Heart Rate (BPM)
                    </Label>
                    <Input
                      id="heartRate"
                      type="number"
                      {...register("heartRate", { valueAsNumber: true })}
                      placeholder="72"
                      data-testid="input-heart-rate"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Normal: 60-100 bpm</p>
                    {errors.heartRate && (
                      <p className="text-sm text-destructive mt-1">{errors.heartRate.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="bloodGlucose" className="block text-sm font-medium text-foreground mb-2">
                      Blood Sugar (mg/dL)
                    </Label>
                    <Input
                      id="bloodGlucose"
                      type="number"
                      {...register("bloodGlucose", { valueAsNumber: true })}
                      placeholder="100"
                      data-testid="input-blood-glucose"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Fasting: 70-100 mg/dL</p>
                    {errors.bloodGlucose && (
                      <p className="text-sm text-destructive mt-1">{errors.bloodGlucose.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="weight" className="block text-sm font-medium text-foreground mb-2">
                      Weight (lbs)
                    </Label>
                    <Input
                      id="weight"
                      type="number"
                      {...register("weight", { valueAsNumber: true })}
                      placeholder="170"
                      data-testid="input-weight"
                    />
                    {errors.weight && (
                      <p className="text-sm text-destructive mt-1">{errors.weight.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="temperature" className="block text-sm font-medium text-foreground mb-2">
                      Temperature (°F)
                    </Label>
                    <Input
                      id="temperature"
                      type="number"
                      step="0.1"
                      {...register("temperature", { valueAsNumber: true })}
                      placeholder="98.6"
                      data-testid="input-temperature"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Normal: 97-99°F</p>
                    {errors.temperature && (
                      <p className="text-sm text-destructive mt-1">{errors.temperature.message}</p>
                    )}
                  </div>
                  
                  <div className="md:col-span-2">
                    <Label htmlFor="notes" className="block text-sm font-medium text-foreground mb-2">
                      Notes (Optional)
                    </Label>
                    <Textarea
                      id="notes"
                      {...register("notes")}
                      rows={3}
                      placeholder="Any symptoms, medication changes, or other observations..."
                      data-testid="textarea-notes"
                    />
                  </div>
                </div>
                
                <div className="mt-8 flex space-x-4">
                  <Button
                    type="submit"
                    disabled={addVitalsMutation.isPending}
                    data-testid="button-submit-vitals"
                  >
                    {addVitalsMutation.isPending ? "Submitting..." : "Submit Vitals"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate("/")}
                    data-testid="button-cancel"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Vitals Charts */}
          <div className="space-y-6">
            {vitalsHistory.length > 0 ? (
              <>
                <VitalsChart data={vitalsHistory} metric="bp" />
                <VitalsChart data={vitalsHistory} metric="heartRate" />
              </>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-muted-foreground">
                    No vitals history available. Start by entering your first reading!
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
