from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_db
from app.models.user import User
from app.models.patient import Patient
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current authenticated user from JWT token."""
    
    if not credentials:
        raise AuthenticationError("Token required")
    
    # Verify token
    payload = verify_token(credentials.credentials)
    if not payload:
        raise AuthenticationError("Invalid token")
    
    # Extract user info
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is disabled")
    
    return user


async def get_current_patient(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Patient:
    """Get current patient profile (only for patient users)."""
    
    if current_user.role != "patient":
        raise AuthorizationError("Patient access required")
    
    # Get patient profile
    result = await db.execute(select(Patient).where(Patient.user_id == current_user.id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise AuthenticationError("Patient profile not found")
    
    return patient


def require_role(required_role: str):
    """Dependency factory to require specific user role."""
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise AuthorizationError(f"Role '{required_role}' required")
        return current_user
    
    return role_checker


def require_roles(*required_roles: str):
    """Dependency factory to require one of multiple roles."""
    
    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise AuthorizationError(f"One of roles {required_roles} required")
        return current_user
    
    return roles_checker


async def get_patient_or_doctor_access(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Patient:
    """Get patient if current user is the patient or a doctor."""
    
    # Get patient
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise AuthenticationError("Patient not found")
    
    # Check access permissions
    if current_user.role == "doctor":
        # Doctors can access any patient
        return patient
    elif current_user.role == "patient":
        # Patients can only access their own data
        if patient.user_id != current_user.id:
            raise AuthorizationError("Access denied")
        return patient
    else:
        raise AuthorizationError("Insufficient permissions")


# Aliases for commonly used dependencies
RequirePatient = Depends(require_role("patient"))
RequireDoctor = Depends(require_role("doctor"))
RequireAdmin = Depends(require_role("admin"))
RequireDoctorOrAdmin = Depends(require_roles("doctor", "admin"))
