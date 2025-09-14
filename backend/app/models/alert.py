from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AlertSeverity(str, enum.Enum):
    MILD = "mild"
    SERIOUS = "serious"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    ANOMALY = "anomaly"
    DRUG_INTERACTION = "drug_interaction"
    RISK_THRESHOLD = "risk_threshold"
    VITAL_EMERGENCY = "vital_emergency"
    MEDICATION_ADHERENCE = "medication_adherence"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Alert details
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    type = Column(Enum(AlertType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status tracking
    acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    alert_metadata = Column(JSON, nullable=True)  # Additional context data
    recommendation = Column(Text, nullable=True)  # Recommended action
    
    # Priority and routing
    priority_score = Column(Integer, default=0)  # For sorting/prioritization
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned doctor
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="alerts")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
