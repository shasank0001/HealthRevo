# HealthRevo Backend

FastAPI-based backend for the HealthRevo AI Health Monitoring system.

## Features

- **JWT Authentication** with role-based access control
- **PostgreSQL Database** with async SQLAlchemy
- **OCR Processing** for prescription analysis using Tesseract
- **Risk Assessment** using heuristic algorithms
- **Alert System** for anomaly detection
- **Drug Interaction Checking** 
- **AI Chatbot Integration** with Google Gemini
- **RESTful API** with automatic documentation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for development)
- Tesseract OCR
- Docker (optional)

### Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database:**
   ```bash
   # For development, SQLite is used by default
   # For production, configure PostgreSQL in .env
   ```

6. **Seed sample data:**
   ```bash
   python scripts/seed_data.py
   ```

7. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

This will start:
- Backend API on port 8000
- PostgreSQL on port 5432
- Redis on port 6379 (optional)

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login

### Patients
- `GET /patients/` - List patients (doctors only)
- `GET /patients/{id}` - Get patient details

### Vitals
- `POST /patients/{id}/vitals` - Add vital signs
- `GET /patients/{id}/vitals` - Get vitals history

### Prescriptions
- `POST /patients/{id}/prescription/upload` - Upload prescription
- `GET /patients/{id}/prescriptions` - Get prescriptions

### Risk Assessment
- `POST /patients/{id}/compute_risk` - Compute risk scores
- `GET /patients/{id}/risk_scores` - Get risk history

### Alerts
- `GET /alerts` - Get alerts (with filters)
- `POST /alerts/{id}/acknowledge` - Acknowledge alert

### Drug Checking
- `POST /drug-check` - Check drug interactions

### AI Chat
- `POST /patients/{id}/chat` - Chat with AI assistant

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── dependencies.py      # FastAPI dependencies
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API routes
│   ├── services/            # Business logic
│   ├── core/                # Core utilities
│   └── utils/               # Helper functions
├── scripts/                 # Utility scripts
├── tests/                   # Test files
├── uploads/                 # File uploads
├── data/                    # Static data
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## Development

### Sample Users

After running the seed script, you can use these credentials:

**Doctor:**
- Email: `doctor@healthrevo.com`
- Password: `doctor123`

**Patients:**
- Email: `john.doe@email.com` / Password: `patient123`
- Email: `jane.smith@email.com` / Password: `patient123`
- Email: `mike.wilson@email.com` / Password: `patient123`

### Environment Variables

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./healthrevo.db

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google Gemini (for chatbot)
GOOGLE_GEMINI_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash

# OCR
TESSERACT_CMD=/usr/bin/tesseract

# File uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
isort app/
flake8 app/
```

## Deployment

### Production Environment

1. **Set up PostgreSQL database**
2. **Configure environment variables for production**
3. **Use Docker or deploy to cloud platform**
4. **Set up reverse proxy (nginx)**
5. **Enable HTTPS**

### Health Check

The API provides a health check endpoint:
```
GET /health
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints
5. Follow FastAPI best practices

## License

MIT License
