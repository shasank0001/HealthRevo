import { User, Vitals, Alert, ChatMessage, Prescription, DrugInteractionResult } from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getAuthToken(): string | null {
  return localStorage.getItem("authToken");
}

function decodeJwtPayload<T = any>(token: string): T | null {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(errorData.detail || `API request failed: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Auth endpoints
  async login(email: string, password: string): Promise<User> {
    // Backend may return only token, so handle both shapes
    const response = await apiRequest<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    const token: string | undefined = response.access_token;
    if (!token) {
      throw new Error("Login response missing access token");
    }
    localStorage.setItem("authToken", token);

    // If user object provided (fallback mode), use it
    if (response.user) {
      const user: User = {
        id: String(response.user.id),
        email: response.user.email,
        fullName: response.user.fullName,
        role: response.user.role,
        createdAt: new Date(),
      };
      localStorage.setItem("authUser", JSON.stringify(user));
      return user;
    }

    // Otherwise, decode JWT to get basic info
    const payload = decodeJwtPayload<{ sub: string; email?: string; role?: User["role"] }>(token);
    const user: User = {
      id: payload?.sub ?? "",
      email: payload?.email ?? email,
      fullName: payload?.email ?? email,
      role: (payload?.role as User["role"]) ?? "patient",
      createdAt: new Date(),
    };
    localStorage.setItem("authUser", JSON.stringify(user));
    return user;
  },

  async logout(): Promise<void> {
    // Clear stored auth data
    localStorage.removeItem("authUser");
    localStorage.removeItem("authToken");
  },

  async getCurrentUser(): Promise<User | null> {
    const storedUser = localStorage.getItem("authUser");
    if (storedUser) return JSON.parse(storedUser);
    const token = getAuthToken();
    if (!token) return null;
    const payload = decodeJwtPayload<{ sub: string; email?: string; role?: User["role"] }>(token);
    if (!payload) return null;
    const user: User = {
      id: payload.sub,
      email: payload.email ?? "",
      fullName: payload.email ?? "",
      role: (payload.role as User["role"]) ?? "patient",
      createdAt: new Date(),
    };
    localStorage.setItem("authUser", JSON.stringify(user));
    return user;
  },

  // Patient endpoints
  async getCurrentPatient(): Promise<any> {
    return apiRequest("/patients/me");
  },

  // Prescriptions
  async getPrescriptions(patientId: string): Promise<Prescription[]> {
    return apiRequest<Prescription[]>(`/patients/${patientId}/prescriptions`);
  },

  async uploadPrescription(patientId: string, data: { ocrText?: string }): Promise<Prescription> {
    return apiRequest<Prescription>(`/patients/${patientId}/prescriptions`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async adjustPrescription(patientId: string, prescriptionId: string, updates: any): Promise<Prescription> {
    return apiRequest<Prescription>(`/patients/${patientId}/prescriptions/${prescriptionId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
  },

  // Vitals endpoints
  async getVitals(patientId: string): Promise<Vitals[]> {
    const vitals = await apiRequest<any[]>(`/patients/${patientId}/vitals`);
    
    // Convert backend response to frontend Vitals type
    return vitals.map(vital => ({
      id: vital.id.toString(),
      patientId: vital.patientId.toString(),
      recordedAt: new Date(vital.recordedAt),
      systolic: vital.systolic,
      diastolic: vital.diastolic,
      heartRate: vital.heartRate,
      temperature: vital.temperature,
      bloodGlucose: vital.bloodGlucose,
      oxygenSaturation: vital.oxygenSaturation,
      weight: vital.weight,
      notes: vital.notes,
      createdAt: new Date(),
    }));
  },

  async getLatestVitals(patientId: string): Promise<Vitals | null> {
    const vital = await apiRequest<any | null>(`/patients/${patientId}/vitals/latest`);
    if (!vital) return null;
    return {
      id: vital.id.toString(),
      patientId: vital.patientId.toString(),
      recordedAt: new Date(vital.recordedAt),
      systolic: vital.systolic,
      diastolic: vital.diastolic,
      heartRate: vital.heartRate,
      temperature: vital.temperature,
      bloodGlucose: vital.bloodGlucose,
      oxygenSaturation: vital.oxygenSaturation,
      weight: vital.weight,
      notes: vital.notes,
      createdAt: new Date(),
    };
  },

  async addVitals(patientId: string, vitals: Partial<Vitals>): Promise<Vitals> {
    const response = await apiRequest<any>(`/patients/${patientId}/vitals`, {
      method: "POST",
      body: JSON.stringify({
        systolic: vitals.systolic,
        diastolic: vitals.diastolic,
        heartRate: vitals.heartRate,
        temperature: vitals.temperature,
        bloodGlucose: vitals.bloodGlucose,
        oxygenSaturation: vitals.oxygenSaturation,
        weight: vitals.weight,
        notes: vitals.notes,
      }),
    });

    return {
      id: response.id.toString(),
      patientId: response.patientId.toString(),
      recordedAt: new Date(response.recordedAt),
      systolic: response.systolic,
      diastolic: response.diastolic,
      heartRate: response.heartRate,
      temperature: response.temperature,
      bloodGlucose: response.bloodGlucose,
      oxygenSaturation: response.oxygenSaturation,
      weight: response.weight,
      notes: response.notes,
      createdAt: new Date(),
    };
  },

  // Alerts endpoints
  async getAlerts(patientId?: string, severity?: Alert["severity"]): Promise<Alert[]> {
    const params = new URLSearchParams();
    if (patientId) params.set("patient_id", String(patientId));
    if (severity) params.set("severity", severity);
    const qs = params.toString() ? `?${params.toString()}` : "";
    const alerts = await apiRequest<any[]>(`/alerts${qs}`);
    
    // Convert backend response to frontend Alert type (values already aligned)
    return alerts.map(alert => ({
      id: String(alert.id),
      patientId: String(alert.patientId),
      generatedAt: alert.generatedAt ? new Date(alert.generatedAt) : new Date(),
      severity: alert.severity,
      type: alert.type,
      message: alert.message ?? alert.title ?? "",
      acknowledged: Boolean(alert.acknowledged),
      metadata: alert.metadata ?? alert.alert_metadata ?? null,
    }));
  },

  async acknowledgeAlert(alertId: string): Promise<void> {
    await apiRequest(`/alerts/${alertId}`, {
      method: "PATCH",
      body: JSON.stringify({ acknowledged: true }),
    });
  },

  // Chat endpoints
  async sendChatMessage(patientId: string, message: string): Promise<ChatMessage> {
    const response = await apiRequest<{
      response: string;
      timestamp: string;
    }>(`/patients/${patientId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });

    return {
      role: "assistant",
      content: response.response,
      timestamp: new Date(response.timestamp),
    };
  },

  // Drug checker
  async checkDrugInteractions(medications: Array<{ name: string; dose: string; frequency: string }>): Promise<{ interactions: DrugInteractionResult[] } > {
    return apiRequest<{ interactions: DrugInteractionResult[] }>(`/drug-check`, {
      method: "POST",
      body: JSON.stringify({ medications }),
    });
  },

  // Patients (doctor)
  async listPatients(): Promise<Array<{ id: string; email: string; fullName?: string; patientId?: string }>> {
    try {
      const data = await apiRequest<any[]>(`/patients/overview`);
      return data.map((u) => ({
        id: String(u.patientId ?? u.id ?? u.userId ?? ""),
        patientId: String(u.patientId ?? u.id ?? ""),
        email: u.email,
        fullName: u.full_name ?? u.fullName ?? "",
      }));
    } catch {
      // Fallback to legacy endpoint
      const data = await apiRequest<any[]>(`/patients/`);
      return data.map((u) => ({
        id: String(u.id ?? u.userId ?? ""),
        patientId: String(u.id ?? u.userId ?? ""),
        email: u.email,
        fullName: u.full_name ?? u.fullName ?? "",
      }));
    }
  },

  async getPatient(patientId: string): Promise<any> {
    return apiRequest<any>(`/patients/${patientId}`);
  },

  async getPatientHistory(patientId: string): Promise<{ vitals: any[]; prescriptions: any[]; alerts: any[] }> {
    const [vitals, prescriptions, alerts] = await Promise.all([
      this.getVitals(patientId),
      this.getPrescriptions(patientId),
      this.getAlerts(patientId),
    ]);
    return { vitals, prescriptions, alerts };
  },

  // Aggregate prescriptions across all patients (doctor)
  async listAllPrescriptions(): Promise<Array<
    {
      id: string;
      patientId: string;
      patientName?: string;
      patientEmail?: string;
      uploadedAt?: string;
      parsedMedications?: { name: string; dose?: string; frequency?: string; instructions?: string }[];
      flags?: any[];
  analysis?: any;
    }
  >> {
    const patients = await this.listPatients();
    const results = await Promise.all(
      patients.map(async (p) => {
        try {
          const pres = await this.getPrescriptions(p.id);
          return pres.map((pr) => ({
            id: String((pr as any).id ?? ""),
            patientId: String((pr as any).patientId ?? p.id),
            patientName: p.fullName,
            patientEmail: p.email,
            uploadedAt: (pr as any).uploadedAt,
            parsedMedications: (pr as any).parsedMedications || [],
            flags: (pr as any).flags || [],
            analysis: (pr as any).analysis,
          }));
        } catch (e) {
          return [] as any[];
        }
      })
    );
    return results.flat();
  },

  // Risk scores (safe fallback if not implemented)
  async getRiskScores(patientId: string): Promise<any[]> {
    try {
      return await apiRequest<any[]>(`/patients/${patientId}/risk-scores`);
    } catch (e: any) {
      // If endpoint not available yet, return empty list to keep UI working
      return [];
    }
  },
};
