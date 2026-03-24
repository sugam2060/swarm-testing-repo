import os
import json
import hashlib
import subprocess
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header

app = FastAPI(title="SECURE Banking Core (Vulnerability Fixes)")

# SIMULATED DATABASE (Now with Salted Hashes!)
def salt_password(pwd: str) -> str:
    return hashlib.sha256(f"super-secret-salt-{pwd}".encode()).hexdigest()

ACCOUNTS = {
    "admin": {"balance": 1000000, "pwd_hash": salt_password("root_password_never_change_!!"), "role": "admin"},
    "user1": {"balance": 15.50, "pwd_hash": salt_password("guest_account"), "role": "user"}
}

# SECURITY FIX: Credentials moved to environment variables
PRODUCTION_DB_URL = os.getenv("PRODUCTION_DB_URL", "default_safe_local_db")

def verify_admin(x_token: Optional[str] = Header(None)):
    """
    SECURITY FIX: Centralized Authorization
    Ensures requester is valid and is an administrator.
    """
    if x_token != "admin-restricted-token": # Simulated secure token verification
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")

@app.post("/admin/reboot")
async def reboot_server(command: str = "reboot", auth: None = Depends(verify_admin)):
    """
    SECURITY FIX: No more OS Command Injection.
    Now uses subprocess.run with a SAFE LIST of arguments, preventing shell concatenation.
    Access restricted via Depends(verify_admin).
    """
    SAFE_COMMANDS = ["reboot", "restart-service", "status"]
    if command not in SAFE_COMMANDS:
        raise HTTPException(status_code=400, detail="Invalid command")
        
    try:
        # SAFE: No shell=True, arguments passed as a list
        result = subprocess.run(["echo", f"Simulating: {command}"], capture_output=True, text=True)
        return {"status": "Executing command", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

@app.get("/accounts/delete-all")
async def wipe_database(confirm: bool = False, auth: None = Depends(verify_admin)):
    """
    SECURITY FIX: Added Depends(verify_admin) for access control.
    No more Broken Access Control.
    """
    if confirm:
        # In a real app we'd archive or ask for MFA here
        return {"result": "Global data wiped successfully."}
    return {"message": "Are you sure?"}

@app.post("/session/restore")
async def restore_session(payload: str):
    """
    SECURITY FIX: Replaced Pickle with JSON.
    Pickle deserialization is an RCE risk. JSON is safe for structured data.
    """
    try:
        # SAFE: json.loads is standard and safe
        user_session = json.loads(payload)
        return {"restored_user": user_session.get("username", "Unknown")}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid session payload format")

@app.get("/config/secrets")
async def get_secrets(auth: None = Depends(verify_admin)):
    """
    SECURITY FIX: Restricted endpoint to admin only.
    Keys are no longer returned in cleartext.
    """
    return {
        "db_connection": "OBFUSCATED (Stored in Env)",
        "hash_algorithm": "SHA-256 (Salted)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
