from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_async_db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import Vitals
from app.models.risk_score import RiskScore
from app.dependencies import get_current_user, get_patient_or_doctor_access, get_current_patient
from app.models.prescription import Prescription
from app.models.alert import Alert
from app.services.gemini_chat_service import GeminiChatService
from app.core.exceptions import ProcessingError, NotFoundError

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    model: str
    success: bool


@router.post("/{patient_id}/chat", response_model=ChatResponse)
async def chat_with_ai(
    patient_id: int,
    chat_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Chat with AI assistant about patient health data."""
    
    # Verify access to patient data
    patient = await get_patient_or_doctor_access(patient_id, current_user, db)
    
    # Get recent vitals (last 7 days)
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    
    vitals_result = await db.execute(
        select(Vitals)
        .where(Vitals.patient_id == patient_id)
        .where(Vitals.recorded_at >= week_ago)
        .order_by(Vitals.recorded_at.desc())
        .limit(10)
    )
    recent_vitals = vitals_result.scalars().all()
    
    # Get recent risk scores
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.patient_id == patient_id)
        .order_by(RiskScore.computed_at.desc())
        .limit(5)
    )
    recent_risk_scores = risk_result.scalars().all()
    
    # Extract chat history from context if provided and enrich with recent prescriptions and alerts
    chat_history = chat_data.context.get("chat_history", []) if chat_data.context else []

    pres_result = await db.execute(
        select(Prescription)
        .where(Prescription.patient_id == patient_id)
        .order_by(Prescription.uploaded_at.desc())
        .limit(5)
    )
    recent_prescriptions = pres_result.scalars().all()

    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.patient_id == patient_id)
        .order_by(Alert.generated_at.desc())
        .limit(5)
    )
    recent_alerts = alerts_result.scalars().all()
    
    try:
        # Initialize Gemini chat service
        chat_service = GeminiChatService()

        # Generate AI response
        result = await chat_service.chat_with_patient(
            message=chat_data.message,
            patient=patient,
            recent_vitals=list(recent_vitals),
            recent_risk_scores=list(recent_risk_scores),
            chat_history=chat_history + [
                {"role": "system", "content": f"Recent prescriptions: {len(recent_prescriptions)}; Recent alerts: {len(recent_alerts)}"}
            ]
        )

        if not result["success"]:
            # Gracefully return fallback response without 500
            return ChatResponse(
                response=result.get("response") or "I'm sorry, I'm having trouble processing your request right now.",
                timestamp=datetime.fromisoformat(result["timestamp"]),
                model=result.get("model", "local-fallback"),
                success=False,
            )

        return ChatResponse(
            response=result["response"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
            model=result["model"],
            success=result["success"]
        )

    except Exception as e:
        # Do not fail the request; return safe fallback
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            timestamp=datetime.utcnow(),
            model="local-fallback",
            success=False,
        )


@router.post("/me/chat", response_model=ChatResponse)
async def chat_with_ai_me(
    chat_data: ChatMessage,
    current_patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_async_db)
):
    """Chat with AI assistant for the authenticated patient (no patient_id needed)."""

    # Use the current authenticated patient
    patient_id = current_patient.id

    # Get recent vitals (last 7 days)
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)

    vitals_result = await db.execute(
        select(Vitals)
        .where(Vitals.patient_id == patient_id)
        .where(Vitals.recorded_at >= week_ago)
        .order_by(Vitals.recorded_at.desc())
        .limit(10)
    )
    recent_vitals = vitals_result.scalars().all()

    # Get recent risk scores
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.patient_id == patient_id)
        .order_by(RiskScore.computed_at.desc())
        .limit(5)
    )
    recent_risk_scores = risk_result.scalars().all()

    # Extract chat history from context if provided
    chat_history = chat_data.context.get("chat_history", []) if chat_data.context else []

    try:
        chat_service = GeminiChatService()
        result = await chat_service.chat_with_patient(
            message=chat_data.message,
            patient=current_patient,
            recent_vitals=list(recent_vitals),
            recent_risk_scores=list(recent_risk_scores),
            chat_history=chat_history
        )
        if not result["success"]:
            return ChatResponse(
                response=result.get("response") or "I'm sorry, I'm having trouble processing your request right now.",
                timestamp=datetime.fromisoformat(result["timestamp"]),
                model=result.get("model", "local-fallback"),
                success=False,
            )

        return ChatResponse(
            response=result["response"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
            model=result["model"],
            success=result["success"]
        )
    except Exception as e:
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            timestamp=datetime.utcnow(),
            model="local-fallback",
            success=False,
        )


@router.post("/{patient_id}/health-summary")
async def generate_health_summary(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate AI-powered health summary for patient."""
    
    # Verify access to patient data
    patient = await get_patient_or_doctor_access(patient_id, current_user, db)
    
    # Get recent vitals (last 30 days)
    from datetime import timedelta
    month_ago = datetime.now() - timedelta(days=30)
    
    vitals_result = await db.execute(
        select(Vitals)
        .where(Vitals.patient_id == patient_id)
        .where(Vitals.recorded_at >= month_ago)
        .order_by(Vitals.recorded_at.desc())
    )
    recent_vitals = vitals_result.scalars().all()
    
    # Get recent risk scores
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.patient_id == patient_id)
        .order_by(RiskScore.computed_at.desc())
        .limit(10)
    )
    recent_risk_scores = risk_result.scalars().all()
    
    try:
        # Initialize Gemini chat service
        chat_service = GeminiChatService()
        
        # Generate health summary
        summary = await chat_service.generate_health_summary(
            patient=patient,
            vitals_data=list(recent_vitals),
            risk_scores=list(recent_risk_scores)
        )
        
        return {
            "summary": summary,
            "generated_at": datetime.utcnow(),
            "vitals_count": len(recent_vitals),
            "risk_scores_count": len(recent_risk_scores)
        }
        
    except Exception as e:
        raise ProcessingError(f"Failed to generate health summary: {str(e)}")
