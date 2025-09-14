"""
Authentication fallback endpoints
"""
from fastapi import FastAPI, HTTPException

def add_auth_endpoints(app: FastAPI, prefix: str):
    """Add authentication fallback endpoints"""
    
    @app.post(f"{prefix}/login")
    async def login(credentials: dict):
        """Login endpoint"""
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        
        # Test with seeded users
        if email == "doctor@healthrevo.com" and password == "doctor123":
            return {
                "access_token": "test_doctor_token",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": email,
                    "fullName": "Dr. Sarah Johnson",
                    "role": "doctor"
                }
            }
        elif password == "patient123" and email in ["john.doe@email.com", "jane.smith@email.com", "mike.wilson@email.com"]:
            user_map = {
                "john.doe@email.com": {"id": 2, "fullName": "John Doe"},
                "jane.smith@email.com": {"id": 3, "fullName": "Jane Smith"},
                "mike.wilson@email.com": {"id": 4, "fullName": "Mike Wilson"}
            }
            user_data = user_map[email]
            return {
                "access_token": f"test_patient_{user_data['id']}_token",
                "token_type": "bearer",
                "user": {
                    "id": user_data["id"],
                    "email": email,
                    "fullName": user_data["fullName"],
                    "role": "patient"
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    @app.post(f"{prefix}/logout")
    async def logout():
        """Logout endpoint"""
        return {"message": "Successfully logged out"}
    
    @app.get(f"{prefix}/me")
    async def get_current_user():
        """Get current user info"""
        return {
            "id": 2,
            "email": "john.doe@email.com",
            "fullName": "John Doe",
            "role": "patient"
        }

    print(f"✅ Added auth fallback endpoints at {prefix}")
