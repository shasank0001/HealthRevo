from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LifestyleLog(Base):
    __tablename__ = "lifestyle_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    log_date = Column(Date, nullable=False, index=True)
    
    # Medication adherence
    medication_taken = Column(Boolean, nullable=True)
    missed_doses = Column(Integer, default=0)
    medication_notes = Column(Text, nullable=True)
    
    # Activity and exercise
    steps = Column(Integer, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    exercise_type = Column(String(100), nullable=True)
    
    # Sleep
    sleep_hours = Column(Numeric(4, 2), nullable=True)
    sleep_quality = Column(Integer, nullable=True)  # 1-10 scale
    
    # Diet and nutrition
    water_intake = Column(Numeric(4, 1), nullable=True)  # Liters
    meals_logged = Column(Integer, nullable=True)
    diet_notes = Column(Text, nullable=True)
    
    # Symptoms and mood
    mood_score = Column(Integer, nullable=True)  # 1-10 scale
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    symptoms = Column(Text, nullable=True)
    
    # General notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(Date, server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="lifestyle_logs")
