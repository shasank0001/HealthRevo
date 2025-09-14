from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Vitals(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Vital signs
    systolic = Column(Integer, nullable=True)  # Blood pressure systolic
    diastolic = Column(Integer, nullable=True)  # Blood pressure diastolic
    heart_rate = Column(Integer, nullable=True)  # BPM
    temperature = Column(Numeric(4, 2), nullable=True)  # Celsius
    blood_glucose = Column(Numeric(6, 2), nullable=True)  # mg/dL
    oxygen_saturation = Column(Integer, nullable=True)  # Percentage
    weight = Column(Numeric(5, 2), nullable=True)  # kg
    height = Column(Numeric(5, 2), nullable=True)  # cm
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="vitals")
