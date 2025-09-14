from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    response: str
    timestamp: datetime
    model: str
    success: bool
    
    class Config:
        from_attributes = True


class ChatHistoryEntry(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class HealthSummaryResponse(BaseModel):
    summary: str
    generated_at: datetime
    vitals_count: int
    risk_scores_count: int
    
    class Config:
        from_attributes = True
