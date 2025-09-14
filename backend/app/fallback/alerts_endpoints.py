"""
Alerts fallback endpoints
"""
from fastapi import FastAPI

def add_alerts_endpoints(app: FastAPI, prefix: str):
    """Add alerts fallback endpoints"""
    
    @app.get(f"{prefix}")
    async def get_alerts():
        """Get alerts"""
        return [
            {
                "id": 1,
                "patientId": 2,
                "type": "high_blood_pressure",
                "severity": "medium",
                "title": "High Blood Pressure Alert",
                "message": "Blood pressure reading of 140/90 detected",
                "resolved": False,
                "generatedAt": "2025-09-13T23:44:29",
                "acknowledged": False,
                "metadata": {"systolic": 140, "diastolic": 90}
            },
            {
                "id": 2,
                "patientId": 2,
                "type": "appointment_reminder",
                "severity": "low",
                "title": "Appointment Reminder",
                "message": "Upcoming appointment in 2 days",
                "resolved": False,
                "generatedAt": "2025-09-13T23:44:29",
                "acknowledged": False,
                "metadata": {"appointment_date": "2025-09-15"}
            },
            {
                "id": 3,
                "patientId": 2,
                "type": "medication_reminder",
                "severity": "medium",
                "title": "Medication Reminder",
                "message": "Time to take your evening medication",
                "resolved": False,
                "generatedAt": "2025-09-13T20:00:00",
                "acknowledged": False,
                "metadata": {"medication": "Lisinopril 10mg"}
            }
        ]
    
    @app.patch(f"{prefix}/{{alert_id}}")
    async def update_alert(alert_id: int, update_data: dict):
        """Update alert (acknowledge, resolve, etc.)"""
        return {
            "id": alert_id,
            "updated": True,
            "acknowledged": update_data.get("acknowledged", False),
            "resolved": update_data.get("resolved", False)
        }

    print(f"✅ Added alerts fallback endpoints at {prefix}")
