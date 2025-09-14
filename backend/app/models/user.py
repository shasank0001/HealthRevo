from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .patient import Patient
    from .prescription import Prescription


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    # Store role as simple string to align with existing DB values (e.g., 'doctor')
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - using string references to avoid circular imports
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    uploaded_prescriptions = relationship("Prescription", back_populates="uploaded_by_user")
