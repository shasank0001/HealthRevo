"""
Patient fallback endpoints
"""
from fastapi import FastAPI

def add_patient_endpoints(app: FastAPI, prefix: str):
    """Add patient fallback endpoints"""
    
    @app.get(f"{prefix}/me")
    async def get_current_patient():
        """Get current patient info"""
        return {
            "id": 2,
            "userId": 2,
            "dob": "1990-05-15",
            "gender": "male",
            "phone": "+1234567890",
            "bloodGroup": "O+",
            "emergencyContact": "Emergency Contact 1",
            "medicalHistory": "No major medical history"
        }
    
    @app.get(f"{prefix}/{{patient_id}}/vitals")
    async def get_patient_vitals(patient_id: int):
        """Get patient vitals"""
        return [
            {
                "id": 1,
                "patientId": patient_id,
                "recordedAt": "2025-09-12T23:44:29",
                "systolic": 120,
                "diastolic": 80,
                "heartRate": 72,
                "temperature": 98.6,
                "bloodGlucose": 95,
                "oxygenSaturation": 98,
                "weight": 70.5,
                "notes": "Normal readings"
            },
            {
                "id": 2,
                "patientId": patient_id,
                "recordedAt": "2025-09-13T23:44:29",
                "systolic": 125,
                "diastolic": 82,
                "heartRate": 75,
                "temperature": 98.4,
                "bloodGlucose": 92,
                "oxygenSaturation": 97,
                "weight": 70.3,
                "notes": "Slightly elevated blood pressure"
            }
        ]
    
    @app.post(f"{prefix}/{{patient_id}}/vitals")
    async def add_patient_vitals(patient_id: int, vitals: dict):
        """Add new vitals"""
        return {
            "id": 999,
            "patientId": patient_id,
            "recordedAt": "2025-09-13T23:45:00",
            "created": True,
            **vitals
        }
    
    @app.get(f"{prefix}/{{patient_id}}/risk-scores")
    async def get_patient_risk_scores(patient_id: int):
        """Get patient risk scores"""
        return {
            "cardiovascular": {
                "score": 0.25,
                "level": "moderate",
                "factors": ["elevated_bp", "family_history"]
            },
            "diabetes": {
                "score": 0.15,
                "level": "low",
                "factors": ["normal_glucose"]
            },
            "overall": {
                "score": 0.20,
                "level": "low-moderate",
                "recommendation": "Continue monitoring vitals, maintain healthy lifestyle"
            }
        }

    print(f"✅ Added patient fallback endpoints at {prefix}")
