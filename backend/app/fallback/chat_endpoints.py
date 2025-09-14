"""
Chat fallback endpoints
"""
from fastapi import FastAPI
import random

def add_chat_endpoints(app: FastAPI, prefix: str):
    """Add chat fallback endpoints"""
    
    @app.post("/patients/{patient_id}/chat")
    async def chat_with_ai(patient_id: int, message_data: dict):
        """Chat with AI assistant"""
        user_message = message_data.get("message", "")
        
        # Simple mock responses based on message content
        responses = {
            "blood pressure": "Your recent blood pressure readings show some elevation. I recommend monitoring daily and discussing with your doctor if it remains high.",
            "medication": "It's important to take medications as prescribed. If you're experiencing side effects, please consult your healthcare provider.",
            "vitals": "Your vital signs are being monitored. Recent trends show stable readings with minor fluctuations that are within normal ranges.",
            "appointment": "Your next appointment is scheduled soon. Make sure to prepare any questions you have for your doctor.",
            "diet": "Maintaining a healthy diet can significantly impact your health metrics. Consider reducing sodium intake for better blood pressure control.",
            "exercise": "Regular physical activity can help improve your overall health and manage conditions like high blood pressure.",
            "symptoms": "If you're experiencing unusual symptoms, please monitor them and contact your healthcare provider if they persist or worsen.",
            "default": [
                "I understand your concern about your health. Based on your recent vitals, I can help provide general guidance.",
                "Your health metrics are being monitored continuously. Is there a specific aspect you'd like to discuss?",
                "I'm here to help you understand your health data. What specific information would you like to know about?",
                "Based on your recent readings, I can provide insights about your health trends. What would you like to focus on?",
                "I can help explain your health metrics and provide general wellness advice. What's your main concern today?"
            ]
        }
        
        # Check for keywords in user message
        response = None
        user_message_lower = user_message.lower()
        
        for keyword, keyword_response in responses.items():
            if keyword != "default" and keyword in user_message_lower:
                response = keyword_response
                break
        
        # Use default responses if no keyword matched
        if not response:
            response = random.choice(responses["default"])
        
        return {
            "response": response,
            "timestamp": "2025-09-13T23:45:00"
        }

    print(f"✅ Added chat fallback endpoints")
