#!/usr/bin/env python3
"""
Simple database seeding script that avoids circular import issues.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_simple_data():
    """Seed database with simple sample data using raw SQL."""
    
    async with AsyncSessionLocal() as session:
        try:
            now = datetime.now().replace(microsecond=0)
            doctor_hash = pwd_context.hash("doctor123")
            patient_hash = pwd_context.hash("patient123")
            
            # Create sample users one by one
            await session.execute(text("""
                INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('doctor@healthrevo.com', :hash, 'Dr. Sarah Johnson', 'doctor', 1, :now)
            """), {"hash": doctor_hash, "now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('john.doe@email.com', :hash, 'John Doe', 'patient', 1, :now)
            """), {"hash": patient_hash, "now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('jane.smith@email.com', :hash, 'Jane Smith', 'patient', 1, :now)
            """), {"hash": patient_hash, "now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active, created_at)
                VALUES ('mike.wilson@email.com', :hash, 'Mike Wilson', 'patient', 1, :now)
            """), {"hash": patient_hash, "now": now})
            
            # Create sample patients using actual column names
            await session.execute(text("""
                INSERT OR IGNORE INTO patients (user_id, dob, gender, phone, blood_group, emergency_contact, medical_history, created_at)
                VALUES (2, '1990-05-15', 'male', '+1234567890', 'O+', 'Emergency Contact 1', 'No major medical history', :now)
            """), {"now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO patients (user_id, dob, gender, phone, blood_group, emergency_contact, medical_history, created_at)
                VALUES (3, '1985-08-22', 'female', '+1234567891', 'A+', 'Emergency Contact 2', 'Hypertension', :now)
            """), {"now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO patients (user_id, dob, gender, phone, blood_group, emergency_contact, medical_history, created_at)
                VALUES (4, '1992-12-03', 'male', '+1234567892', 'B+', 'Emergency Contact 3', 'Diabetes Type 2', :now)
            """), {"now": now})
            
            # Create sample vitals using actual column names
            yesterday = now - timedelta(days=1)
            
            await session.execute(text("""
                INSERT OR IGNORE INTO vitals (patient_id, systolic, diastolic, heart_rate, temperature, weight, height, recorded_at, created_at)
                VALUES (1, 120, 80, 72, 98.6, 70.5, 175.0, :recorded, :created)
            """), {"recorded": yesterday, "created": yesterday})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO vitals (patient_id, systolic, diastolic, heart_rate, temperature, weight, height, recorded_at, created_at)
                VALUES (2, 140, 90, 85, 99.1, 65.2, 162.0, :recorded, :created)
            """), {"recorded": yesterday, "created": yesterday})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO vitals (patient_id, systolic, diastolic, heart_rate, temperature, weight, height, recorded_at, created_at)
                VALUES (3, 110, 70, 68, 98.2, 80.1, 180.0, :recorded, :created)
            """), {"recorded": yesterday, "created": yesterday})
            
            # Create sample alerts using actual column names
            await session.execute(text("""
                INSERT OR IGNORE INTO alerts (patient_id, type, severity, title, message, resolved, created_at)
                VALUES (2, 'high_blood_pressure', 'medium', 'High Blood Pressure Alert', 'Blood pressure reading of 140/90 detected', 0, :now)
            """), {"now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO alerts (patient_id, type, severity, title, message, resolved, created_at)
                VALUES (1, 'appointment_reminder', 'low', 'Appointment Reminder', 'Upcoming appointment in 2 days', 0, :now)
            """), {"now": now})
            
            # Add some sample risk scores
            await session.execute(text("""
                INSERT OR IGNORE INTO risk_scores (patient_id, risk_type, score, risk_level, method, created_at)
                VALUES (2, 'cardiovascular', 75.5, 'high', 'framingham', :now)
            """), {"now": now})
            
            await session.execute(text("""
                INSERT OR IGNORE INTO risk_scores (patient_id, risk_type, score, risk_level, method, created_at)
                VALUES (3, 'diabetes', 45.2, 'medium', 'ada_guidelines', :now)
            """), {"now": now})
            
            await session.commit()
            print("✅ Sample data seeded successfully")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


async def main():
    """Main function to seed the database."""
    print("🌱 Seeding database with simple sample data...")
    await seed_simple_data()
    
    print("\n📧 Sample login credentials:")
    print("Doctor: doctor@healthrevo.com / doctor123")
    print("Patient 1: john.doe@email.com / patient123")
    print("Patient 2: jane.smith@email.com / patient123")
    print("Patient 3: mike.wilson@email.com / patient123")


if __name__ == "__main__":
    asyncio.run(main())
