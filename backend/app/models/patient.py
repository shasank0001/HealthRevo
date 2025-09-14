from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    phone = Column(String(30), nullable=True)
    blood_group = Column(String(10), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    medical_history = Column(String, nullable=True)  # JSON string or text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    vitals = relationship("Vitals", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")
    lifestyle_logs = relationship("LifestyleLog", back_populates="patient", cascade="all, delete-orphan")
