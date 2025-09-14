"""
Simple FastAPI server for HealthRevo backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="HealthRevo API",
    version="1.0.0",
    description="AI-powered health monitoring and prescription analysis system",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HealthRevo API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": "HealthRevo API", "version": "1.0.0"}

# Simple authentication endpoint
@app.post("/auth/login")
async def login(credentials: dict):
    """Login endpoint"""
    email = credentials.get("email", "")
    password = credentials.get("password", "")
    
    # Test with seeded users
    if email == "doctor@healthrevo.com" and password == "doctor123":
        return {
            "access_token": "test_doctor_token",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": email,
                "fullName": "Dr. Sarah Johnson",
                "role": "doctor"
            }
        }
    elif password == "patient123" and email in ["john.doe@email.com", "jane.smith@email.com", "mike.wilson@email.com"]:
        user_map = {
            "john.doe@email.com": {"id": 2, "fullName": "John Doe"},
            "jane.smith@email.com": {"id": 3, "fullName": "Jane Smith"},
            "mike.wilson@email.com": {"id": 4, "fullName": "Mike Wilson"}
        }
        user_data = user_map[email]
        return {
            "access_token": f"test_patient_{user_data['id']}_token",
            "token_type": "bearer",
            "user": {
                "id": user_data["id"],
                "email": email,
                "fullName": user_data["fullName"],
                "role": "patient"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/patients/me")
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
            "weight": 70.3,
            "notes": "Slightly elevated"
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

@app.get("/alerts")
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
            "acknowledged": False
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
            "acknowledged": False
        }
    ]

@app.patch("/alerts/{alert_id}")
async def update_alert(alert_id: int, update_data: dict):
    """Update alert (acknowledge, resolve, etc.)"""
    return {
        "id": alert_id,
        "updated": True,
        "acknowledged": update_data.get("acknowledged", False),
        "resolved": update_data.get("resolved", False)
    }

@app.post("/patients/{patient_id}/chat")
async def chat_with_ai(patient_id: int, message_data: dict):
    """Chat with AI assistant"""
    user_message = message_data.get("message", "")
    
    # Simple mock responses
    responses = [
        "I understand your concern about your health. Based on your recent vitals, everything looks normal.",
        "Your blood pressure readings are within acceptable ranges. Keep monitoring daily.",
        "I recommend maintaining your current medication schedule and healthy lifestyle.",
        "Your health metrics show positive trends. Continue with your current routine.",
        "Consider discussing any concerns with your doctor during your next appointment."
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        "response": response,
        "timestamp": "2025-09-13T23:45:00"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
