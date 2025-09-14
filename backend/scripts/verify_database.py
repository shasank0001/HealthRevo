#!/usr/bin/env python3
"""
Simple database verification script for HealthRevo.
"""

import sqlite3
import sys
import os

# Database path
db_path = "/home/shasank/shasank/Hackathon/supersus/HealthRevo/backend/healthrevo.db"

def test_database():
    """Test database structure and data."""
    print("🚀 HealthRevo Database Verification")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check tables exist
        print("📋 Checking database tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'patients', 'vitals', 'alerts', 'risk_scores', 
                          'prescriptions', 'lifestyle_logs', 'drug_interactions', 'alembic_version']
        
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} - MISSING")
        
        # Test 2: Check data counts
        print("\n📊 Checking data counts...")
        data_checks = [
            ("users", 4),
            ("patients", 3),
            ("vitals", 3),
            ("alerts", 2),
            ("risk_scores", 2)
        ]
        
        for table, expected_count in data_checks:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual_count = cursor.fetchone()[0]
            
            if actual_count >= expected_count:
                print(f"   ✅ {table}: {actual_count} records")
            else:
                print(f"   ⚠️  {table}: {actual_count} records (expected {expected_count})")
        
        # Test 3: Check sample data
        print("\n👥 Sample users:")
        cursor.execute("SELECT email, full_name, role FROM users ORDER BY role, email")
        users = cursor.fetchall()
        
        for email, name, role in users:
            print(f"   • {role.upper()}: {name} ({email})")
        
        # Test 4: Check relationships
        print("\n🔗 Testing relationships...")
        cursor.execute("""
            SELECT u.email, p.gender, p.blood_group 
            FROM users u 
            JOIN patients p ON u.id = p.user_id 
            WHERE u.role = 'patient'
        """)
        patient_data = cursor.fetchall()
        
        print(f"   ✅ Patient relationships: {len(patient_data)} records")
        for email, gender, blood_group in patient_data:
            print(f"      - {email}: {gender}, {blood_group}")
        
        # Test 5: Check vitals with patient info
        cursor.execute("""
            SELECT u.email, v.systolic, v.diastolic, v.heart_rate 
            FROM vitals v
            JOIN patients p ON v.patient_id = p.id
            JOIN users u ON p.user_id = u.id
        """)
        vitals_data = cursor.fetchall()
        
        print(f"\n📈 Vitals data: {len(vitals_data)} records")
        for email, systolic, diastolic, hr in vitals_data:
            print(f"      - {email}: {systolic}/{diastolic} mmHg, HR {hr}")
        
        # Test 6: Check alerts
        cursor.execute("""
            SELECT u.email, a.type, a.severity, a.title
            FROM alerts a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
        """)
        alert_data = cursor.fetchall()
        
        print(f"\n🚨 Alerts: {len(alert_data)} records")
        for email, alert_type, severity, title in alert_data:
            print(f"      - {email}: {severity.upper()} - {title}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Database verification completed successfully!")
        
        print("\n🎯 Sample login credentials:")
        print("   Doctor: doctor@healthrevo.com / doctor123")
        print("   Patient 1: john.doe@email.com / patient123")
        print("   Patient 2: jane.smith@email.com / patient123")
        print("   Patient 3: mike.wilson@email.com / patient123")
        
        print("\n🚀 Ready to start the backend server!")
        print("   Command: uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False


if __name__ == "__main__":
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Run: python setup_database.py")
        sys.exit(1)
    
    success = test_database()
    sys.exit(0 if success else 1)
