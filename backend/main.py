"""
HealthRevo API Backend - Main Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import random

# Create FastAPI app
app = FastAPI(
    title="HealthRevo API",
    version="1.0.0",
    description="AI-powered health monitoring and prescription analysis system",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to HealthRevo API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": "HealthRevo API",
        "version": "1.0.0"
    }

# Authentication endpoints
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

# Patient endpoints
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

# Alerts endpoints
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

@app.patch("/alerts/{alert_id}")
async def update_alert(alert_id: int, update_data: dict):
    """Update alert (acknowledge, resolve, etc.)"""
    return {
        "id": alert_id,
        "updated": True,
        "acknowledged": update_data.get("acknowledged", False),
        "resolved": update_data.get("resolved", False)
    }

# Chat endpoints
@app.post("/patients/{patient_id}/chat")
async def chat_with_ai(patient_id: int, message_data: dict):
    """Chat with AI assistant"""
    user_message = message_data.get("message", "")
    
    # Simple mock responses based on message content
    responses = {
        "blood pressure": "Your recent blood pressure readings show some elevation. I recommend monitoring daily and discussing with your doctor if it remains high.",
        "medication": "It's important to take medications as prescribed. If you're experiencing side effects, please consult your healthcare provider.",
        "vitals": "Your vital signs are being monitored. Recent trends show stable readings with minor fluctuations that are within normal ranges.",
        "appointment": "Your next appointment is scheduled soon. Make sure to prepare any questions you have for your doctor.",
        "diet": "Maintaining a healthy diet can significantly impact your health metrics. Consider reducing sodium intake for better blood pressure control.",
        "exercise": "Regular physical activity can help improve your overall health and manage conditions like high blood pressure.",
        "symptoms": "If you're experiencing unusual symptoms, please monitor them and contact your healthcare provider if they persist or worsen.",
        "default": [
            "I understand your concern about your health. Based on your recent vitals, I can help provide general guidance.",
            "Your health metrics are being monitored continuously. Is there a specific aspect you'd like to discuss?",
            "I'm here to help you understand your health data. What specific information would you like to know about?",
            "Based on your recent readings, I can provide insights about your health trends. What would you like to focus on?",
            "I can help explain your health metrics and provide general wellness advice. What's your main concern today?"
        ]
    }
    
    # Check for keywords in user message
    response = None
    user_message_lower = user_message.lower()
    
    for keyword, keyword_response in responses.items():
        if keyword != "default" and keyword in user_message_lower:
            response = keyword_response
            break
    
    # Use default responses if no keyword matched
    if not response:
        response = random.choice(responses["default"])
    
    return {
        "response": response,
        "timestamp": "2025-09-13T23:45:00"
    }

# Risk scores endpoint
@app.get("/patients/{patient_id}/risk-scores")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
