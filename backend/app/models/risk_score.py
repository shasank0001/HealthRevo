from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Risk assessment
    risk_type = Column(String(50), nullable=False)  # "diabetes", "hypertension", "heart_disease", etc.
    score = Column(Numeric(5, 2), nullable=False)  # 0-100 risk score
    risk_level = Column(String(20), nullable=False)  # "low", "moderate", "high", "critical"
    
    # Explanation and factors
    drivers = Column(JSON, nullable=True)  # Key factors contributing to risk
    recommendations = Column(JSON, nullable=True)  # Recommended actions
    
    # Calculation metadata
    method = Column(String(50), nullable=False)  # "heuristic-v1", "ml-model-v1", etc.
    confidence_score = Column(Numeric(5, 2), nullable=True)  # Model confidence 0-100
    data_quality_score = Column(Numeric(5, 2), nullable=True)  # Quality of input data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="risk_scores")
