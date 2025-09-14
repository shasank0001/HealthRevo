#!/usr/bin/env python3
"""
Test script to verify HealthRevo backend functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.auth import AuthService
from app.core.security import verify_password
from sqlalchemy import text


async def test_authentication():
    """Test user authentication."""
    print("🔐 Testing authentication...")
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        # Test doctor login
        doctor_token = await auth_service.authenticate_user("doctor@healthrevo.com", "doctor123")
        if doctor_token:
            print("✅ Doctor authentication successful")
        else:
            print("❌ Doctor authentication failed")
        
        # Test patient login
        patient_token = await auth_service.authenticate_user("john.doe@email.com", "patient123")
        if patient_token:
            print("✅ Patient authentication successful")
        else:
            print("❌ Patient authentication failed")
        
        # Test invalid login
        invalid_token = await auth_service.authenticate_user("invalid@email.com", "wrongpass")
        if not invalid_token:
            print("✅ Invalid login correctly rejected")
        else:
            print("❌ Invalid login incorrectly accepted")


async def test_database_relationships():
    """Test database relationships and data integrity."""
    print("\n🔗 Testing database relationships...")
    
    async with AsyncSessionLocal() as session:
        # Test user-patient relationship
        result = await session.execute(text("""
            SELECT u.email, u.full_name, p.gender, p.blood_group 
            FROM users u 
            JOIN patients p ON u.id = p.user_id 
            WHERE u.role = 'patient'
        """))
        
        patients = result.fetchall()
        if len(patients) >= 3:
            print(f"✅ Found {len(patients)} patient records with proper relationships")
            for patient in patients:
                print(f"   - {patient[1]} ({patient[0]}) - {patient[2]}, {patient[3]}")
        else:
            print("❌ Missing patient relationship data")
        
        # Test vitals data
        result = await session.execute(text("""
            SELECT p.user_id, v.systolic, v.diastolic, v.heart_rate, v.recorded_at
            FROM vitals v
            JOIN patients p ON v.patient_id = p.id
        """))
        
        vitals = result.fetchall()
        if len(vitals) >= 3:
            print(f"✅ Found {len(vitals)} vital records")
        else:
            print("❌ Missing vitals data")
        
        # Test alerts
        result = await session.execute(text("""
            SELECT a.type, a.severity, a.title, p.user_id
            FROM alerts a
            JOIN patients p ON a.patient_id = p.id
        """))
        
        alerts = result.fetchall()
        if len(alerts) >= 2:
            print(f"✅ Found {len(alerts)} alert records")
        else:
            print("❌ Missing alerts data")


async def test_google_gemini_config():
    """Test Google Gemini configuration."""
    print("\n🤖 Testing Google Gemini configuration...")
    
    try:
        from app.services.gemini_chat import GeminiChatService
        from app.config import settings
        
        if settings.google_api_key:
            print("✅ Google API key is configured")
            
            # Initialize service (don't make actual API call to avoid quota)
            gemini_service = GeminiChatService()
            print("✅ GeminiChatService initialized successfully")
            
        else:
            print("⚠️  Google API key not configured in environment")
            
    except Exception as e:
        print(f"❌ Error testing Gemini configuration: {e}")


async def test_risk_calculation():
    """Test risk calculation logic."""
    print("\n📊 Testing risk calculation...")
    
    try:
        from app.services.risk_calculator import RiskCalculator
        
        # Sample vital signs for testing
        sample_vitals = {
            'systolic_bp': 140,
            'diastolic_bp': 90,
            'heart_rate': 85,
            'temperature': 99.1,
            'weight': 65.2,
            'height': 162.0
        }
        
        # Sample patient data
        sample_patient = {
            'age': 38,  # Born 1985
            'gender': 'female',
            'medical_history': 'Hypertension'
        }
        
        risk_calc = RiskCalculator()
        risk_score = risk_calc.calculate_cardiovascular_risk(sample_vitals, sample_patient)
        
        if risk_score >= 0:
            print(f"✅ Risk calculation successful: {risk_score}")
        else:
            print("❌ Risk calculation failed")
            
    except Exception as e:
        print(f"❌ Error testing risk calculation: {e}")


async def run_all_tests():
    """Run all backend tests."""
    print("🚀 HealthRevo Backend Test Suite")
    print("=" * 50)
    
    try:
        await test_authentication()
        await test_database_relationships()
        await test_google_gemini_config()
        await test_risk_calculation()
        
        print("\n" + "=" * 50)
        print("✅ Backend test suite completed!")
        print("\n🎯 Next steps:")
        print("   1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("   2. Visit http://localhost:8000/docs for API documentation")
        print("   3. Test the frontend integration")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
