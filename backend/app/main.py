"""
HealthRevo API - Main Application
FastAPI application with proper router organization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path

# Add the backend directory to Python path for proper imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import settings
try:
    from app.config import settings
except ImportError:
    # Fallback settings if config is not available
    class Settings:
        app_name = "HealthRevo API"
        app_version = "1.0.0"
        debug = True
        cors_origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]
        upload_dir = "./uploads"
    settings = Settings()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered health monitoring and prescription analysis system",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Mount static files (for uploaded files)
    try:
        app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")

    # Include routers
    # Ensure SQLAlchemy models are imported so relationships resolve
    try:
        import importlib
        importlib.import_module("app.models")  # ensure models are registered
    except Exception as e:
        print(f"⚠️  Could not pre-import models: {e}")

    # Include routers
    setup_routers(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Add basic endpoints
    setup_basic_endpoints(app)
    
    return app

def setup_routers(app: FastAPI):
    """Setup and include all routers"""
    
    # Import and include routers with error handling
    routers_config = [
        ("auth", "app.routers.auth", "/auth", ["Authentication"]),
        ("patients", "app.routers.patients", "/patients", ["Patients"]),
        # Patient-scoped feature routers should live under /patients
        ("vitals", "app.routers.vitals", "/patients", ["Vitals"]),
        ("chat", "app.routers.chat", "/patients", ["Chat"]),
        ("prescriptions", "app.routers.prescriptions", "/patients", ["Prescriptions"]),
        ("risk_scores", "app.routers.risk_scores", "/patients", ["Risk Scores"]),
        # Global resources
        ("alerts", "app.routers.alerts", "/alerts", ["Alerts"]),
        ("drug_checker", "app.routers.drug_checker", "/drug-check", ["Drug Checker"]),
    ]
    
    for router_name, module_path, prefix, tags in routers_config:
        try:
            import importlib
            module = importlib.import_module(module_path)
            # Include router if available
            app.include_router(module.router, prefix=prefix, tags=tags)
            print(f"✅ Included {router_name} router at {prefix}")

            # If router has no routes defined, add fallback endpoints
            try:
                routes_count = len(getattr(module, "router", None).routes)
            except Exception:
                routes_count = 0

            if routes_count == 0:
                print(f"⚠️  {router_name} router has no endpoints; adding fallbacks")
                add_fallback_endpoints(app, router_name, prefix)
        except ImportError as e:
            print(f"⚠️  {router_name} router not available: {e}")
            # Add fallback endpoints for missing routers
            add_fallback_endpoints(app, router_name, prefix)
        except Exception as e:
            print(f"❌ Failed to include {router_name} router: {e}")

def add_fallback_endpoints(app: FastAPI, router_name: str, prefix: str):
    """Add fallback endpoints when routers are not available"""
    
    if router_name == "auth":
        from app.fallback.auth_endpoints import add_auth_endpoints
        add_auth_endpoints(app, prefix)
    elif router_name == "patients":
        from app.fallback.patient_endpoints import add_patient_endpoints
        add_patient_endpoints(app, prefix)
    elif router_name == "vitals":
        from app.fallback.vitals_endpoints import add_vitals_endpoints
        add_vitals_endpoints(app, prefix)
    elif router_name == "alerts":
        from app.fallback.alerts_endpoints import add_alerts_endpoints
        add_alerts_endpoints(app, prefix)
    elif router_name == "chat":
        from app.fallback.chat_endpoints import add_chat_endpoints
        add_chat_endpoints(app, prefix)
    elif router_name == "prescriptions":
        # No explicit fallback implemented yet
        print("ℹ️  No fallback for prescriptions")
    elif router_name == "risk_scores":
        # No explicit fallback implemented yet
        print("ℹ️  No fallback for risk scores")
    elif router_name == "drug_checker":
        # No explicit fallback implemented yet
        print("ℹ️  No fallback for drug checker")

def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers"""
    try:
        from app.core.exceptions import setup_exception_handlers
        setup_exception_handlers(app)
    except ImportError:
        print("⚠️  Custom exception handlers not available, using defaults")

def setup_basic_endpoints(app: FastAPI):
    """Setup basic health and info endpoints"""
    
    @app.get("/")
    async def root():
        """Root endpoint returning API information"""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs" if settings.debug else "Documentation disabled in production"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version
        }

# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
