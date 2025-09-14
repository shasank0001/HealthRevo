#!/usr/bin/env python3
"""
HealthRevo Backend Startup Script
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Main startup function"""
    try:
        import uvicorn
        # Ensure working directory is backend so relative paths (e.g., ./healthrevo.db) resolve correctly
        os.chdir(str(backend_dir))
        os.environ.setdefault("PYTHONPATH", str(backend_dir))
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(backend_dir)],
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("If uvicorn is missing, install dependencies with: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
