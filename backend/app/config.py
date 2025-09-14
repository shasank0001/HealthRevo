from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "HealthRevo API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./healthrevo.db"
    database_url_sync: str = "sqlite:///./healthrevo.db"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours
    
    # Google Gemini
    google_gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    
    # File uploads
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    # OCR
    tesseract_cmd: str = "/usr/bin/tesseract"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # DrugBank
    drugbank_data_path: str = "./data/drugbank_interactions.csv"
    
    # Risk calculation
    risk_calculation_window_days: int = 7
    anomaly_threshold_percentage: int = 20
    
    # Email (for future use)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
