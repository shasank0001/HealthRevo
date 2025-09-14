from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # OCR and parsing results
    ocr_text = Column(Text, nullable=True)  # Raw OCR output
    parsed_medications = Column(JSON, nullable=True)  # List of medication objects
    flags = Column(JSON, nullable=True)  # Interaction warnings, dose flags, etc.
    
    # File information
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)  # Path to stored file
    file_size = Column(Integer, nullable=True)
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, error
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    uploaded_by_user = relationship("User", back_populates="uploaded_prescriptions")
