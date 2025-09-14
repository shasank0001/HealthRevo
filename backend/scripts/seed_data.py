"""
Seed script to populate the database with sample data for development and testing.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal, Base, async_engine
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.vitals import Vitals
from app.models.risk_score import RiskScore
from app.models.alert import Alert, AlertSeverity, AlertType
from app.core.security import get_password_hash


async def create_sample_users():
    """Create sample users and patients."""
    
    async with AsyncSessionLocal() as session:
        # Create sample doctor
        doctor = User(
            email="doctor@healthrevo.com",
            password_hash=get_password_hash("doctor123"),
            full_name="Dr. Sarah Johnson",
            role=UserRole.DOCTOR
        )
        session.add(doctor)
        
        # Create sample patients
        patients_data = [
            {
                "email": "john.doe@email.com",
                "full_name": "John Doe",
                "dob": "1980-05-15",
                "gender": "male",
                "phone": "+1-555-0101",
                "blood_group": "O+"
            },
            {
                "email": "jane.smith@email.com", 
                "full_name": "Jane Smith",
                "dob": "1975-08-22",
                "gender": "female",
                "phone": "+1-555-0102",
                "blood_group": "A-"
            },
            {
                "email": "mike.wilson@email.com",
                "full_name": "Mike Wilson", 
                "dob": "1990-12-03",
                "gender": "male",
                "phone": "+1-555-0103",
                "blood_group": "B+"
            }
        ]
        
        for patient_data in patients_data:
            # Create user account
            user = User(
                email=patient_data["email"],
                password_hash=get_password_hash("patient123"),
                full_name=patient_data["full_name"],
                role=UserRole.PATIENT
            )
            session.add(user)
            await session.flush()
            
            # Create patient profile
            patient = Patient(
                user_id=user.id,
                dob=datetime.strptime(patient_data["dob"], "%Y-%m-%d").date(),
                gender=patient_data["gender"],
                phone=patient_data["phone"],
                blood_group=patient_data["blood_group"]
            )
            session.add(patient)
        
        await session.commit()
        print("✅ Sample users and patients created")


async def create_sample_vitals():
    """Create sample vitals data."""
    
    async with AsyncSessionLocal() as session:
        # Get all patients
        from sqlalchemy import select
        result = await session.execute(select(Patient))
        patients = result.scalars().all()
        
        for patient in patients:
            # Create vitals for the last 30 days
            for days_ago in range(30, 0, -1):
                recorded_date = datetime.now() - timedelta(days=days_ago)
                
                # Simulate different health patterns for each patient
                if patient.id == 1:  # John Doe - Hypertension risk
                    systolic = 140 + (days_ago % 10)
                    diastolic = 90 + (days_ago % 5)
                    heart_rate = 75 + (days_ago % 8)
                    blood_glucose = 95 + (days_ago % 15)
                elif patient.id == 2:  # Jane Smith - Diabetes risk  
                    systolic = 125 + (days_ago % 8)
                    diastolic = 80 + (days_ago % 6)
                    heart_rate = 70 + (days_ago % 10)
                    blood_glucose = 140 + (days_ago % 20)
                else:  # Mike Wilson - Normal values
                    systolic = 120 + (days_ago % 5)
                    diastolic = 78 + (days_ago % 4)
                    heart_rate = 68 + (days_ago % 6)
                    blood_glucose = 85 + (days_ago % 10)
                
                vital = Vitals(
                    patient_id=patient.id,
                    recorded_at=recorded_date,
                    systolic=systolic,
                    diastolic=diastolic,
                    heart_rate=heart_rate,
                    temperature=Decimal("36.5") + Decimal(str((days_ago % 3) * 0.2)),
                    blood_glucose=Decimal(str(blood_glucose)),
                    oxygen_saturation=97 + (days_ago % 3),
                    weight=Decimal("70.0") + Decimal(str((days_ago % 5) * 0.1))
                )
                session.add(vital)
        
        await session.commit()
        print("✅ Sample vitals data created")


async def create_sample_risk_scores():
    """Create sample risk scores."""
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Patient))
        patients = result.scalars().all()
        
        risk_types = ["hypertension", "diabetes", "heart_disease"]
        
        for patient in patients:
            for risk_type in risk_types:
                # Simulate different risk levels
                if patient.id == 1 and risk_type == "hypertension":
                    score = 75.5  # High risk
                    risk_level = "high"
                elif patient.id == 2 and risk_type == "diabetes":
                    score = 68.2  # High risk
                    risk_level = "high"
                else:
                    score = 25.0 + (patient.id * 10)  # Moderate risk
                    risk_level = "moderate"
                
                risk_score = RiskScore(
                    patient_id=patient.id,
                    risk_type=risk_type,
                    score=Decimal(str(score)),
                    risk_level=risk_level,
                    drivers={"sample": "data"},
                    method="heuristic-v1",
                    confidence_score=Decimal("85.0")
                )
                session.add(risk_score)
        
        await session.commit()
        print("✅ Sample risk scores created")


async def create_sample_alerts():
    """Create sample alerts."""
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Patient))
        patients = result.scalars().all()
        
        # Create some alerts for high-risk patients
        alerts_data = [
            {
                "patient_id": 1,
                "severity": AlertSeverity.SERIOUS,
                "type": AlertType.RISK_THRESHOLD,
                "title": "Hypertension Risk Alert",
                "message": "Blood pressure consistently elevated over the past week",
                "recommendation": "Schedule appointment with healthcare provider"
            },
            {
                "patient_id": 2,
                "severity": AlertSeverity.MILD,
                "type": AlertType.ANOMALY,
                "title": "Blood Glucose Anomaly",
                "message": "Blood glucose readings higher than usual pattern",
                "recommendation": "Monitor dietary intake and medication adherence"
            }
        ]
        
        for alert_data in alerts_data:
            alert = Alert(
                patient_id=alert_data["patient_id"],
                severity=alert_data["severity"],
                type=alert_data["type"],
                title=alert_data["title"],
                message=alert_data["message"],
                recommendation=alert_data["recommendation"],
                alert_metadata={"source": "sample_data"}
            )
            session.add(alert)
        
        await session.commit()
        print("✅ Sample alerts created")


async def main():
    """Main function to run all seed operations."""
    
    print("🌱 Starting database seeding...")
    
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("📊 Database tables created")
    
    # Create sample data
    await create_sample_users()
    await create_sample_vitals()
    await create_sample_risk_scores()
    await create_sample_alerts()
    
    print("🎉 Database seeding completed successfully!")
    print("")
    print("Sample login credentials:")
    print("Doctor: doctor@healthrevo.com / doctor123")
    print("Patient 1: john.doe@email.com / patient123")
    print("Patient 2: jane.smith@email.com / patient123")
    print("Patient 3: mike.wilson@email.com / patient123")


if __name__ == "__main__":
    asyncio.run(main())
