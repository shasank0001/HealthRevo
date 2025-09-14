#!/usr/bin/env python3
"""
Database setup script for HealthRevo backend.
This script initializes the database and optionally seeds it with sample data.
"""

import asyncio
import sys
import os
import subprocess
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, async_engine, Base
from app.config import settings


async def check_database_connection():
    """Check if database connection is working."""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def run_migrations():
    """Run Alembic migrations to create/update database schema."""
    try:
        print("🔄 Running database migrations...")
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


async def seed_database():
    """Seed database with sample data."""
    try:
        print("🌱 Seeding database with sample data...")
        
        # Import and run seed functions
        from scripts.seed_data import (
            create_sample_users,
            create_sample_vitals,
            create_sample_risk_scores,
            create_sample_alerts
        )
        
        await create_sample_users()
        await create_sample_vitals()
        await create_sample_risk_scores()
        await create_sample_alerts()
        
        print("✅ Database seeding completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        return False


async def initialize_database(seed_data=True):
    """Initialize the database with schema and optional sample data."""
    
    print("🚀 Starting database initialization...")
    print(f"📊 Database URL: {settings.database_url}")
    
    # Step 1: Run migrations
    if not run_migrations():
        return False
    
    # Step 2: Check connection
    if not await check_database_connection():
        return False
    
    # Step 3: Seed data (optional)
    if seed_data:
        if not await seed_database():
            print("⚠️  Database seeding failed, but database schema is ready")
            return True
    
    print("🎉 Database initialization completed successfully!")
    return True


async def reset_database():
    """Reset database by dropping all tables and recreating them."""
    
    print("⚠️  WARNING: This will delete all data in the database!")
    
    try:
        # Drop all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("🗑️  All tables dropped")
        
        # Recreate tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("📊 All tables recreated")
        
        print("✅ Database reset completed")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False


def print_usage():
    """Print usage instructions."""
    print("""
HealthRevo Database Setup Script

Usage:
    python setup_database.py [command]

Commands:
    init            Initialize database with migrations and sample data (default)
    init-no-seed    Initialize database without sample data
    seed            Seed database with sample data only
    reset           Reset database (drops all tables and recreates)
    check           Check database connection
    help            Show this help message

Examples:
    python setup_database.py                    # Initialize with sample data
    python setup_database.py init-no-seed       # Initialize without sample data
    python setup_database.py seed               # Add sample data only
    python setup_database.py reset              # Reset database
    """)


async def main():
    """Main function to handle command line arguments."""
    
    command = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    if command == "help":
        print_usage()
        return
    
    elif command == "init":
        success = await initialize_database(seed_data=True)
        
    elif command == "init-no-seed":
        success = await initialize_database(seed_data=False)
        
    elif command == "seed":
        success = await check_database_connection()
        if success:
            success = await seed_database()
        
    elif command == "reset":
        response = input("Are you sure you want to reset the database? (yes/no): ")
        if response.lower() == "yes":
            success = await reset_database()
            if success:
                success = await initialize_database(seed_data=True)
        else:
            print("Database reset cancelled")
            return
        
    elif command == "check":
        success = await check_database_connection()
        
    else:
        print(f"Unknown command: {command}")
        print_usage()
        return
    
    if success:
        print("✅ Operation completed successfully")
        
        # Print sample credentials if data was seeded
        if command in ["init", "reset"]:
            print("\n📧 Sample login credentials:")
            print("Doctor: doctor@healthrevo.com / doctor123")
            print("Patient 1: john.doe@email.com / patient123")
            print("Patient 2: jane.smith@email.com / patient123")
            print("Patient 3: mike.wilson@email.com / patient123")
            
    else:
        print("❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
