from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(255), nullable=False, index=True)
    drug_b = Column(String(255), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # "minor", "moderate", "major", "contraindicated"
    description = Column(Text, nullable=False)
    mechanism = Column(Text, nullable=True)  # How the interaction occurs
    clinical_management = Column(Text, nullable=True)  # What to do about it
    
    # DrugBank specific fields
    drugbank_id_a = Column(String(20), nullable=True)
    drugbank_id_b = Column(String(20), nullable=True)
    
    # Alternative names for fuzzy matching
    drug_a_aliases = Column(Text, nullable=True)  # JSON array of alternative names
    drug_b_aliases = Column(Text, nullable=True)  # JSON array of alternative names
