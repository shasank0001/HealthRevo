from typing import Dict, List, Optional
try:
    import google.generativeai as genai
except Exception:  # Module may not be installed; fallback mode will be used
    genai = None
from app.config import settings
from app.models.patient import Patient
from app.models.vitals import Vitals
from app.models.risk_score import RiskScore
import json
from datetime import datetime


class GeminiChatService:
    """Google Gemini AI chat service for patient health assistance.
    Falls back to a local templated response if API key is not set.
    """
    
    def __init__(self):
        # Configure Gemini API if available
        self._use_gemini = False
        try:
            if settings.google_gemini_api_key and genai is not None:
                genai.configure(api_key=settings.google_gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                self._use_gemini = True
        except Exception:
            # Fallback to local mode
            self._use_gemini = False
    
    async def chat_with_patient(
        self,
        message: str,
        patient: Patient,
        recent_vitals: List[Vitals] = None,
        recent_risk_scores: List[RiskScore] = None,
        chat_history: List[Dict] = None,
        patient_name: str | None = None,
    ) -> Dict[str, str]:
        """
        Generate AI response for patient question using Gemini.
        
        Args:
            message: Patient's question/message
            patient: Patient object with profile info
            recent_vitals: Recent vital signs data
            recent_risk_scores: Recent risk assessment scores
            chat_history: Previous chat messages for context
            
        Returns:
            Dict with AI response and metadata
        """
        
        try:
            # Build context prompt with patient data
            system_prompt = self._build_system_prompt(
                patient, recent_vitals, recent_risk_scores, patient_name=patient_name
            )
            
            # Build conversation history
            conversation_context = self._build_conversation_context(
                chat_history, message
            )
            
            # Combine system prompt with conversation
            full_prompt = f"{system_prompt}\n\n{conversation_context}"
            
            # Generate response using Gemini or fallback
            if self._use_gemini:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                        top_p=0.8,
                        top_k=40
                    )
                )
                # Extract response text
                ai_response = response.text if getattr(response, "text", None) else "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            else:
                # Local safe fallback response
                ai_response = (
                    "I’m here to help explain your health data. While I can’t replace medical advice, "
                    "here’s some general guidance based on your recent information. If you’re worried or "
                    "have urgent symptoms, please contact your healthcare provider or emergency services."
                )
            
            return {
                "success": True,
                "response": ai_response,
                "model": settings.gemini_model if self._use_gemini else "local-fallback",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact your healthcare provider for urgent questions.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(
        self,
        patient: Patient,
        recent_vitals: List[Vitals] = None,
        recent_risk_scores: List[RiskScore] = None,
        patient_name: str | None = None,
    ) -> str:
        """Build system prompt with patient context."""
        # Calculate patient age
        age = "unknown"
        if getattr(patient, "dob", None):
            try:
                today = datetime.now().date()
                age = str(today.year - patient.dob.year)
            except Exception:
                pass

        # Format recent vitals summary
        vitals_summary = "No recent vitals data available."
        if recent_vitals:
            try:
                latest_vital = recent_vitals[0]
                vitals_parts: List[str] = []
                if getattr(latest_vital, "systolic", None) and getattr(latest_vital, "diastolic", None):
                    vitals_parts.append(f"Blood pressure: {latest_vital.systolic}/{latest_vital.diastolic} mmHg")
                if getattr(latest_vital, "heart_rate", None):
                    vitals_parts.append(f"Heart rate: {latest_vital.heart_rate} BPM")
                if getattr(latest_vital, "temperature", None):
                    vitals_parts.append(f"Temperature: {latest_vital.temperature}°C")
                if getattr(latest_vital, "blood_glucose", None):
                    vitals_parts.append(f"Blood glucose: {latest_vital.blood_glucose} mg/dL")
                if getattr(latest_vital, "oxygen_saturation", None):
                    vitals_parts.append(f"Oxygen saturation: {latest_vital.oxygen_saturation}%")
                if vitals_parts:
                    vitals_summary = f"Latest vitals: {', '.join(vitals_parts)}"
            except Exception:
                pass

        # Format risk scores summary
        risk_summary = "No risk assessments available."
        if recent_risk_scores:
            try:
                risk_parts: List[str] = []
                for risk in recent_risk_scores:
                    risk_type = getattr(risk, "risk_type", "Risk")
                    risk_level = getattr(risk, "risk_level", "unknown")
                    score = getattr(risk, "score", "?")
                    risk_parts.append(f"{risk_type}: {risk_level} risk (score: {score})")
                if risk_parts:
                    risk_summary = f"Current risk assessments: {', '.join(risk_parts)}"
            except Exception:
                pass

        name = patient_name or "Patient"

        system_prompt = (
            "You are a helpful medical AI assistant for HealthRevo, designed to help patients understand their health data and provide general health guidance.\n\n"
            "IMPORTANT GUIDELINES:\n"
            "- Always emphasize that you cannot replace professional medical advice\n"
            "- For urgent symptoms or emergencies, direct patients to seek immediate medical care\n"
            "- Provide educational information in simple, understandable language\n"
            "- Be supportive and encouraging while being factually accurate\n"
            "- If unsure about something, recommend consulting with their healthcare provider\n\n"
            "PATIENT CONTEXT:\n"
            f"- Name: {name}\n"
            f"- Age: {age} years\n"
            f"- Gender: {getattr(patient, 'gender', None) or 'Not specified'}\n"
            f"- Blood group: {getattr(patient, 'blood_group', None) or 'Not specified'}\n\n"
            "CURRENT HEALTH DATA:\n"
            f"- {vitals_summary}\n"
            f"- {risk_summary}\n\n"
            "When answering questions:\n"
            "1. Use the patient's health data to provide personalized context when relevant\n"
            "2. Explain medical terms in simple language\n"
            "3. Provide actionable, safe recommendations\n"
            "4. Always remind patients to consult their healthcare provider for medical decisions\n"
            "5. Be empathetic and supportive\n\n"
            "Remember: You are an educational assistant, not a replacement for medical professionals."
        )
        return system_prompt
    
    def _build_conversation_context(
        self,
        chat_history: List[Dict] = None,
        current_message: str = ""
    ) -> str:
        """Build conversation context from chat history."""
        
        context_parts = []
        
        # Add recent chat history (limit to last 5 exchanges)
        if chat_history:
            recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
            
            context_parts.append("RECENT CONVERSATION:")
            for entry in recent_history:
                if entry.get("role") == "user":
                    context_parts.append(f"Patient: {entry.get('content', '')}")
                elif entry.get("role") == "assistant":
                    context_parts.append(f"Assistant: {entry.get('content', '')}")
            
            context_parts.append("")  # Add blank line
        
        # Add current message
        context_parts.append(f"CURRENT QUESTION:\nPatient: {current_message}")
        context_parts.append("\nPlease provide a helpful, accurate, and empathetic response:")
        
        return "\n".join(context_parts)
    
    async def generate_health_summary(
        self,
        patient: Patient,
        vitals_data: List[Vitals],
        risk_scores: List[RiskScore],
        patient_name: str | None = None,
    ) -> str:
        """Generate a health summary for the patient using Gemini."""
        
        try:
            # Build summary prompt
            summary_prompt = f"""Generate a friendly, encouraging health summary for this patient based on their recent data:

Patient: {patient_name or 'Patient'}
Recent vitals count: {len(vitals_data)}
Risk assessments: {len(risk_scores)}

Please create a brief, positive summary that:
1. Highlights any positive trends
2. Notes areas for attention (if any)
3. Provides encouraging, actionable recommendations
4. Uses simple, non-medical language
5. Emphasizes the value of continued monitoring

Keep it under 200 words and focus on empowering the patient."""

            response = self.model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.6,
                    max_output_tokens=300,
                    top_p=0.9
                )
            )
            
            return response.text if response.text else "Your health data shows you're taking great steps in monitoring your wellbeing. Keep up the good work!"
            
        except Exception as e:
            return f"We're monitoring your health progress. Continue tracking your vitals and stay in touch with your healthcare provider."
