# Migration Guide: OpenAI ChatGPT to Google Gemini

This guide outlines the changes made to migrate from OpenAI ChatGPT to Google Gemini for the HealthRevo chatbot functionality.

## Changes Made

### 1. Environment Configuration
- **File**: `.env.example` and `app/config.py`
- **Change**: Replaced OpenAI configuration with Google Gemini
- **Old**: `OPENAI_API_KEY`
- **New**: `GOOGLE_GEMINI_API_KEY` and `GEMINI_MODEL`

### 2. Dependencies
- **File**: `requirements.txt`
- **Change**: Replaced OpenAI library with Google Generative AI
- **Old**: `openai==1.3.7`
- **New**: `google-generativeai==0.3.2`

### 3. Chat Service Implementation
- **File**: `app/services/gemini_chat_service.py` (new)
- **Features**:
  - Google Gemini API integration
  - Context-aware patient health conversations
  - Health summary generation
  - Conversation history management
  - Safety guidelines and medical disclaimers

### 4. API Endpoints
- **File**: `app/routers/chat.py`
- **Updated**: Complete implementation with Gemini integration
- **Endpoints**:
  - `POST /{patient_id}/chat` - Chat with AI assistant
  - `POST /{patient_id}/health-summary` - Generate health summary

### 5. Docker Configuration
- **File**: `docker-compose.yml`
- **Change**: Updated environment variables for Gemini

### 6. Schemas
- **File**: `app/schemas/chat.py` (new)
- **Added**: Pydantic models for chat requests and responses

## Setup Instructions

### 1. Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create a new API key
3. Copy the API key

### 2. Update Environment Variables
```bash
# In your .env file
GOOGLE_GEMINI_API_KEY=your-google-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 4. Update Docker Environment (if using Docker)
The docker-compose.yml has been updated with the new environment variables.

## API Usage Examples

### Chat with AI Assistant
```bash
curl -X POST "http://localhost:8000/patients/1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do my recent blood pressure readings mean?",
    "context": {
      "chat_history": []
    }
  }'
```

### Generate Health Summary
```bash
curl -X POST "http://localhost:8000/patients/1/health-summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Key Differences: OpenAI vs Gemini

| Feature | OpenAI ChatGPT | Google Gemini |
|---------|----------------|---------------|
| API Cost | Token-based pricing | Token-based pricing (competitive) |
| Model Options | GPT-3.5, GPT-4 | Gemini 1.5 Flash, Pro |
| Context Window | Up to 32k tokens | Up to 1M tokens (Gemini 1.5) |
| Safety Features | Built-in content filtering | Google's safety framework |
| Integration | OpenAI Python SDK | Google Generative AI SDK |

## Benefits of Google Gemini

1. **Larger Context Window**: Gemini 1.5 supports up to 1M tokens, allowing for more comprehensive patient history
2. **Competitive Pricing**: Often more cost-effective than OpenAI
3. **Advanced Reasoning**: Strong performance on medical and health-related queries
4. **Built-in Safety**: Google's robust safety and content filtering
5. **Multimodal Capabilities**: Support for text, images, and other formats (future expansion)

## Customization Options

### Model Selection
You can change the Gemini model by updating the `GEMINI_MODEL` environment variable:
- `gemini-1.5-flash` - Fast, efficient for most use cases
- `gemini-1.5-pro` - More capable, higher quality responses

### Generation Parameters
Modify the generation config in `gemini_chat_service.py`:
```python
generation_config=genai.types.GenerationConfig(
    temperature=0.7,     # Creativity (0.0-1.0)
    max_output_tokens=500,  # Response length
    top_p=0.8,          # Nucleus sampling
    top_k=40            # Top-k sampling
)
```

## Testing the Migration

### 1. Basic Chat Test
```python
# Test script
import asyncio
from app.services.gemini_chat_service import GeminiChatService

async def test_chat():
    service = GeminiChatService()
    response = await service.chat_with_patient(
        message="Hello, can you help me understand my health data?",
        patient=mock_patient
    )
    print(response)

asyncio.run(test_chat())
```

### 2. Health Summary Test
Test the health summary generation with sample patient data.

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GOOGLE_GEMINI_API_KEY` is set correctly
   - Verify the API key is active in Google AI Studio

2. **Import Error**
   - Run `pip install google-generativeai`
   - Check Python version compatibility

3. **Rate Limiting**
   - Gemini has rate limits; implement retry logic if needed
   - Monitor usage in Google Cloud Console

### Error Handling
The service includes comprehensive error handling and fallback responses to ensure reliability.

## Future Enhancements

1. **Multimodal Support**: Add image analysis for medical images
2. **Fine-tuning**: Custom model training for medical domain
3. **Caching**: Implement response caching for common queries
4. **Analytics**: Track conversation patterns and effectiveness

## Rollback Instructions

If you need to revert to OpenAI:
1. Restore the original OpenAI configuration
2. Install `openai` package
3. Revert the chat service implementation
4. Update environment variables

The migration maintains the same API interface, so frontend integration remains unchanged.
