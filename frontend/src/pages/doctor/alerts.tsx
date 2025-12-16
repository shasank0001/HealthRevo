import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import type { Alert as AlertT } from "@/types";
import { Navbar } from "@/components/layout/navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useLocation } from "wouter";
import { AlertTriangle, Bell, Phone, FileText, Eye, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const doctorSections = [
  { id: "patients", label: "Patient Overview" },
  { id: "alerts", label: "Alerts & Triage" },
  { id: "prescriptions", label: "Prescription Review" },
  { id: "assistant", label: "AI Assistant" },
];

export default function DoctorAlerts() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();

  const handleSectionChange = (section: string) => {
    navigate(`/${section === "patients" ? "" : section}`);
  };

  // Get all alerts
  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.getAlerts(),
  });

  // Local state for history dialog
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyPatientId, setHistoryPatientId] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyItems, setHistoryItems] = useState<AlertT[]>([]);

  // Acknowledge alert mutation
  const acknowledgeAlertMutation = useMutation({
    mutationFn: async (alertId: string) => {
      await api.acknowledgeAlert(alertId);
    },
    onSuccess: () => {
      toast({
        title: "Alert acknowledged",
        description: "The alert has been marked as acknowledged.",
      });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
    onError: (error) => {
      console.error("Acknowledge alert error:", error);
      toast({
        title: "Failed to acknowledge alert",
        description: "Please try again.",
        variant: "destructive",
      });
    },
  });

  // Categorize alerts by severity
  const criticalAlerts = alerts.filter((alert: any) => alert.severity === "critical");
  const highPriorityAlerts = alerts.filter((alert: any) => alert.severity === "serious");
  const moderateAlerts = alerts.filter((alert: any) => alert.severity === "mild");

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "urgent": return "border-destructive bg-destructive/5";
      case "serious": return "border-accent bg-accent/5";
      case "mild": return "border-secondary bg-secondary/5";
      default: return "border-border";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "urgent": return <Badge variant="destructive">URGENT</Badge>;
      case "serious": return <Badge className="bg-accent text-accent-foreground">HIGH</Badge>;
      case "mild": return <Badge variant="secondary">MODERATE</Badge>;
      default: return <Badge variant="outline">LOW</Badge>;
    }
  };

  const handleAcknowledgeAlert = (alertId: string) => {
    acknowledgeAlertMutation.mutate(alertId);
  };

  const handleViewHistory = async (patientId: string) => {
    setHistoryPatientId(patientId);
    setHistoryOpen(true);
    setHistoryLoading(true);
    try {
      // Fetch alerts scoped to this patient
      const items = await api.getAlerts(String(patientId));
      setHistoryItems(items);
    } catch (e) {
      console.error("History fetch failed", e);
      toast({ title: "Could not load history", variant: "destructive" });
    } finally {
      setHistoryLoading(false);
    }
  };

  // Mock enhanced alert data with patient information
  const enhancedAlerts = alerts.map((alert: any, index: number) => ({
    ...alert,
    patientName: `Patient ${index + 1}`,
    timeAgo: index === 0 ? "2 hours ago" : index === 1 ? "4 hours ago" : "1 day ago",
    recommendation: alert.metadata?.recommendation || "Contact patient for follow-up",
  }));

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar
          title="HealthRevo"
          subtitle="Doctor Panel"
          sections={doctorSections}
          onSectionChange={handleSectionChange}
          currentSection="alerts"
        />
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <>
    <div className="min-h-screen bg-background">
      <Navbar
  title="HealthRevo"
        subtitle="Doctor Panel"
        sections={doctorSections}
        onSectionChange={handleSectionChange}
        currentSection="alerts"
      />

      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Priority Alerts */}
          <div className="lg:col-span-2 space-y-4">
            <Card data-testid="card-priority-alerts">
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold text-foreground mb-4">Priority Alerts</h2>
                
                {enhancedAlerts.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No active alerts at this time.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {enhancedAlerts.map((alert: any, index: number) => (
                      <div
                        key={alert.id}
                        className={`border-l-4 p-4 rounded ${getSeverityColor(alert.severity)}`}
                        data-testid={`alert-${index}`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-medium text-foreground" data-testid={`alert-title-${index}`}>
                              {alert.type === "vitals_anomaly" ? "Vital Signs Alert" : 
                               alert.type === "prescription_flag" ? "Prescription Alert" : 
                               "Health Alert"}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {alert.patientName} - {alert.timeAgo}
                            </p>
                          </div>
                          {getSeverityBadge(alert.severity)}
                        </div>
                        <p className="text-sm text-muted-foreground mb-3" data-testid={`alert-message-${index}`}>
                          {alert.message}
                        </p>
                        {alert.recommendation && (
                          <p className="text-sm text-foreground mb-3 font-medium">
                            Recommendation: {alert.recommendation}
                          </p>
                        )}
                        <div className="flex space-x-2">
                          {alert.severity === "urgent" && (
                            <Button 
                              size="sm" 
                              variant="destructive"
                              data-testid={`button-contact-${index}`}
                            >
                              <Phone className="w-4 h-4 mr-1" />
                              Contact Patient
                            </Button>
                          )}
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleViewHistory(alert.patientId)}
                            data-testid={`button-view-history-${index}`}
                          >
                            <FileText className="w-4 h-4 mr-1" />
                            View History
                          </Button>
                          {!alert.acknowledged && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleAcknowledgeAlert(alert.id)}
                              disabled={acknowledgeAlertMutation.isPending}
                              data-testid={`button-acknowledge-${index}`}
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              {acknowledgeAlertMutation.isPending ? "Acknowledging..." : "Acknowledge"}
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          
          {/* Alert Summary and Quick Actions */}
          <div className="space-y-6">
            <Card data-testid="card-alert-summary">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">Alert Summary</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Critical</span>
                    <Badge variant="destructive" data-testid="badge-critical-count">
                      {criticalAlerts.length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">High Priority</span>
                    <Badge className="bg-accent text-accent-foreground" data-testid="badge-high-count">
                      {highPriorityAlerts.length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Moderate</span>
                    <Badge variant="secondary" data-testid="badge-moderate-count">
                      {moderateAlerts.length}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card data-testid="card-quick-actions">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start" 
                    data-testid="button-bulk-reminders"
                  >
                    <Bell className="w-4 h-4 mr-2" />
                    Send Bulk Reminders
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    data-testid="button-export-report"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Export Alert Report
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    data-testid="button-configure-settings"
                  >
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Configure Alert Settings
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Alert Statistics */}
            <Card data-testid="card-alert-stats">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-4">Today's Activity</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">New Alerts</span>
                    <span className="text-sm font-medium">12</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Acknowledged</span>
                    <span className="text-sm font-medium">8</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Escalated</span>
                    <span className="text-sm font-medium">3</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Resolved</span>
                    <span className="text-sm font-medium">15</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
    {/* History Dialog */}
    <Dialog open={historyOpen} onOpenChange={setHistoryOpen}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Alert History</DialogTitle>
          <DialogDescription>
            Recent alerts for patient {historyPatientId ?? ""}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3 max-h-[60vh] overflow-auto">
          {historyLoading ? (
            <div className="text-sm text-muted-foreground">Loading...</div>
          ) : historyItems.length === 0 ? (
            <div className="text-sm text-muted-foreground">No alert history.</div>
          ) : (
            historyItems.map((item, i) => (
              <div key={i} className={`border rounded p-3 ${getSeverityColor(item.severity)}`}>
                <div className="flex items-center justify-between">
                  <div className="font-medium">
                    {item.type?.toString().replace(/_/g, " ")}
                  </div>
                  {getSeverityBadge(item.severity)}
                </div>
                <div className="text-sm text-muted-foreground mt-1">{item.message}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {new Date(item.generatedAt).toLocaleString()} • {item.acknowledged ? "Acknowledged" : "Unacknowledged"}
                </div>
              </div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
    </>
  );
}
