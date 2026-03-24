from fastapi import FastAPI, HTTPException, Response, Depends, Header
import os
from typing import Optional

app = FastAPI(title="SECURE Internal Admin Tools (Vulnerability Fixes)")

# SIMULATED DATABASE
USER_DATABASE = {
    1: {"name": "Saurav", "email": "saurav@example.com", "is_admin": False},
    2: {"name": "Admin", "email": "admin@paperjetlabs.com", "is_admin": True}
}

# SECURITY FIX: Credentials moved to environment variables (No longer hardcoded!)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "SECURE_STORAGE_KEY_PLACEHOLDER")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

def get_current_user_id(x_user_id: Optional[int] = Header(None)) -> int:
    """
    SECURITY FIX: Authentication Dependency
    Returns the user ID of the requester.
    """
    if not x_user_id or x_user_id not in USER_DATABASE:
        raise HTTPException(status_code=401, detail="Unauthorized: User ID must be provided in headers")
    return x_user_id

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    """
    SECURITY FIX: Profile Access Control (IDOR Fix)
    A user can only view their own profile, unless they are an admin.
    """
    if current_user_id != user_id and not USER_DATABASE[current_user_id]["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Accessing another user's profile is not allowed")
    
    user = USER_DATABASE.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/{user_id}/upgrade")
async def upgrade_user(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    """
    SECURITY FIX: Role-Based Access Control (Missing Authorization Fix)
    Only an administrator can perform user upgrades.
    """
    if not USER_DATABASE[current_user_id]["is_admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Administrator privilege required for upgrades")
        
    user = USER_DATABASE.get(user_id)
    if user:
        user["is_admin"] = True
        return {"status": "User upgraded successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/system/env")
async def get_system_env(current_user_id: int = Depends(get_current_user_id)):
    """
    SECURITY FIX: Information Disclosure Fix
    Endpoint removed or restricted for security reasons.
    """
    raise HTTPException(status_code=405, detail="Accessing the full environment is restricted for security.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
