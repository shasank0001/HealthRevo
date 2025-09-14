"""
Vitals fallback endpoints
"""
from fastapi import FastAPI

def add_vitals_endpoints(app: FastAPI, prefix: str):
    """Add vitals fallback endpoints"""
    
    # Note: Vitals endpoints are usually nested under patients
    # So we'll add them with /patients prefix
    
    @app.get("/patients/{patient_id}/vitals")
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
    
    @app.post("/patients/{patient_id}/vitals")
    async def add_patient_vitals(patient_id: int, vitals: dict):
        """Add new vitals"""
        return {
            "id": 999,
            "patientId": patient_id,
            "recordedAt": "2025-09-13T23:45:00",
            "created": True,
            **vitals
        }

    print(f"✅ Added vitals fallback endpoints")
