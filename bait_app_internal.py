from fastapi import FastAPI, HTTPException, Response
import os

app = FastAPI(title="Bait App: Internal Admin Tools")

# SIMULATED DATABASE
USER_DATABASE = {
    1: {"name": "Saurav", "email": "saurav@example.com", "is_admin": False},
    2: {"name": "Admin", "email": "admin@paperjetlabs.com", "is_admin": True}
}

# CRITICAL VULNERABILITY: Hardcoded AWS Credentials
AWS_SECRET_ACCESS_KEY = "AKIA_FAKE_LONG_SECRET_KEY_FOR_TESTING"
AWS_REGION = "us-east-1"

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int):
    """
    CRITICAL VULNERABILITY: IDOR (Insecure Direct Object Reference)
    The system does not verify that the requester owns the profile.
    Anyone can iterate through 'user_id' to scrape the entire database.
    """
    user = USER_DATABASE.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/{user_id}/upgrade")
async def upgrade_user(user_id: int):
    """
    CRITICAL VULNERABILITY: Missing Authorization
    No checks are performed to ensure only an admin can upgrade users.
    """
    user = USER_DATABASE.get(user_id)
    if user:
        user["is_admin"] = True
        return {"status": "User upgraded to Administrator"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/system/env")
async def get_system_env():
    """
    CRITICAL VULNERABILITY: Information Disclosure
    Exposing environment variables (which likely contain real production keys) via an API.
    """
    return {"env": dict(os.environ)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
