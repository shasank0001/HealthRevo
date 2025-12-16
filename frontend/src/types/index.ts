// Frontend-only types for HealthRevo React app
// These will be replaced when integrating with FastAPI backend

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: "patient" | "doctor" | "admin";
  createdAt: Date;
}

export interface Patient {
  id: string;
  userId: string;
  dob?: string;
  gender?: string;
  phone?: string;
  bloodGroup?: string;
  createdAt: Date;
}

export interface Vitals {
  id: string;
  patientId: string;
  recordedAt: Date;
  systolic?: number;
  diastolic?: number;
  heartRate?: number;
  temperature?: number;
  bloodGlucose?: number;
  oxygenSaturation?: number;
  weight?: number;
  notes?: string;
  createdAt: Date;
}

export interface Prescription {
  id: string;
  patientId: string;
  uploadedBy: string;
  uploadedAt: Date;
  ocrText?: string;
  parsedMedications?: ParsedMedication[];
  flags?: any[];
  analysis?: {
    summary?: string;
    interactions?: Array<{
      severity?: string;
      description?: string;
      drugA?: string;
      drugB?: string;
    }>; 
    findings?: Array<{ message: string; severity?: string; type?: string }>;
  };
  originalFilename?: string;
}

export interface RiskScore {
  id: string;
  patientId: string;
  computedAt: Date;
  riskType: string;
  score: number;
  drivers?: any;
  method: string;
}

export interface Alert {
  id: string;
  patientId: string;
  generatedAt: Date;
  severity: "mild" | "serious" | "urgent" | "critical";
  type: string;
  message: string;
  acknowledged: boolean;
  metadata?: any;
}

export interface LifestyleLog {
  id: string;
  patientId: string;
  logDate: string;
  medicationTaken?: boolean;
  steps?: number;
  sleepHours?: number;
  notes?: string;
}

export interface ParsedMedication {
  name: string;
  dose: string;
  frequency: string;
  instructions?: string;
}

export interface DrugInteractionResult {
  severity: "minor" | "moderate" | "major";
  description: string;
  drugA: string;
  drugB: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}
