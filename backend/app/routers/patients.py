from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from app.database import get_async_db
from app.models.patient import Patient
from app.models.user import User
from app.dependencies import get_current_user, require_role, RequireDoctor
from app.core.exceptions import AuthorizationError, AuthenticationError
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me")
async def get_current_patient(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current patient's profile. Only for users with role 'patient'."""

    if current_user.role != "patient":
        raise AuthorizationError("Patient access required")

    result = await db.execute(select(Patient).where(Patient.user_id == current_user.id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise AuthenticationError("Patient profile not found")

    # Return a minimal schema matching frontend expectations (camelCase)
    return {
        "id": patient.id,
        "userId": patient.user_id,
        "dob": patient.dob.isoformat() if patient.dob else None,
        "gender": patient.gender,
        "phone": patient.phone,
        "bloodGroup": patient.blood_group,
        "emergencyContact": patient.emergency_contact,
        "medicalHistory": patient.medical_history,
    }

@router.get("/", response_model=List[UserResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = RequireDoctor,
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of patients (doctor only)."""
    
    result = await db.execute(
        select(Patient).options(joinedload(Patient.user))
        .join(User)
        .where(User.role == "patient")
        .offset(skip)
        .limit(limit)
    )
    patients = result.scalars().all()

    # Return ORM users; response_model (UserResponse) will serialize from attributes
    return [p.user for p in patients if p.user is not None]


@router.get("/overview")
async def get_patients_overview(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = RequireDoctor,
    db: AsyncSession = Depends(get_async_db)
):
    """Return patient list with both patientId and user info (for doctor dashboards)."""

    result = await db.execute(
        select(Patient).options(joinedload(Patient.user))
        .join(User)
        .where(User.role == "patient")
        .offset(skip)
        .limit(limit)
    )
    patients = result.scalars().all()

    return [
        {
            "id": p.id,  # patient id for convenience
            "patientId": p.id,
            "userId": p.user.id if p.user else None,
            "email": p.user.email if p.user else None,
            "fullName": p.user.full_name if p.user else None,
        }
        for p in patients
    ]


@router.get("/{patient_id}")
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get patient details."""
    # Access control: doctors can access any patient; patients only themselves
    if current_user.role not in ("doctor", "patient"):
        raise AuthorizationError("Access denied")

    result = await db.execute(
        select(Patient).options(joinedload(Patient.user)).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise AuthenticationError("Patient not found")

    if current_user.role == "patient" and patient.user_id != current_user.id:
        raise AuthorizationError("Access denied")

    # Shape response for frontend (camelCase)
    return {
        "id": patient.id,
        "userId": patient.user_id,
        "fullName": patient.user.full_name if getattr(patient, "user", None) else None,
        "email": patient.user.email if getattr(patient, "user", None) else None,
        "dob": patient.dob.isoformat() if patient.dob else None,
        "gender": patient.gender,
        "phone": patient.phone,
        "bloodGroup": patient.blood_group,
        "emergencyContact": patient.emergency_contact,
        "medicalHistory": patient.medical_history,
    }
