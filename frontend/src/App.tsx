import { Switch, Route, Redirect } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import Login from "@/pages/login";
import PatientDashboard from "@/pages/patient/dashboard";
import PatientVitals from "@/pages/patient/vitals";
import PatientMedications from "@/pages/patient/medications";
import PatientAssistant from "@/pages/patient/assistant";
import DoctorDashboard from "@/pages/doctor/dashboard";
import DoctorAlerts from "@/pages/doctor/alerts";
import DoctorPrescriptions from "@/pages/doctor/prescriptions";
import DoctorAssistant from "@/pages/doctor/assistant";
import DoctorPatientDetails from "@/pages/doctor/patient-details";
import NotFound from "@/pages/not-found";

function AppRouter() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <Switch>
        <Route path="/login" component={Login} />
        <Route path="*">
          <Redirect to="/login" />
        </Route>
      </Switch>
    );
  }

  if (user.role === "patient") {
    return (
      <Switch>
        <Route path="/" component={PatientDashboard} />
        <Route path="/vitals" component={PatientVitals} />
        <Route path="/medications" component={PatientMedications} />
        <Route path="/assistant" component={PatientAssistant} />
        <Route path="/login">
          <Redirect to="/" />
        </Route>
        <Route component={NotFound} />
      </Switch>
    );
  }

  if (user.role === "doctor") {
    return (
      <Switch>
        <Route path="/" component={DoctorDashboard} />
  <Route path="/patients/:id" component={DoctorPatientDetails} />
        <Route path="/alerts" component={DoctorAlerts} />
        <Route path="/prescriptions" component={DoctorPrescriptions} />
  <Route path="/assistant" component={DoctorAssistant} />
        <Route path="/login">
          <Redirect to="/" />
        </Route>
        <Route component={NotFound} />
      </Switch>
    );
  }

  return <NotFound />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AuthProvider>
          <Toaster />
          <AppRouter />
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
