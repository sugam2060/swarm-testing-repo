import os
import pickle
import base64
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Bait App: CRITICAL Banking Core")

# SIMULATED DATABASE (Plain Text!)
ACCOUNTS = {
    "admin": {"balance": 1000000, "password": "root_password_never_change_!!"},
    "user1": {"balance": 15.50, "password": "guest_account"}
}

PRODUCTION_DB_URL = "postgresql://superuser:P4ssw0rd_DB_123@10.0.0.1:5432/main"

@app.post("/admin/reboot")
async def reboot_server(passwd: str, command: str = "reboot"):
    """
    CRITICAL VULNERABILITY: OS Command Injection
    Accepts arbitrary bash commands and passes them to os.system.
    Example: ?command=rm -rf /
    """
    if passwd != ACCOUNTS["admin"]["password"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # DEADLY: System-level execution of unsanitized strings
    os.system(f"echo 'Restarting...' && {command}")
    return {"status": "Executing command"}

@app.get("/accounts/delete-all")
async def wipe_database(confirm: bool = False):
    """
    CRITICAL VULNERABILITY: Broken Access Control (IDOR/No Auth)
    An endpoint that deletes all data requires NO authentication.
    """
    if confirm:
        ACCOUNTS.clear()
        return {"result": "Global data wiped successfully."}
    return {"message": "Are you sure?"}

@app.post("/session/restore")
async def restore_session(payload: str):
    """
    CRITICAL VULNERABILITY: Insecure Deserialization
    Uses the 'pickle' module on base64-encoded strings provided by the user.
    An attacker can craft a payload to execute remote shell commands instantly.
    """
    try:
        data = base64.b64decode(payload)
        # RCE: pickle is never safe!
        user_obj = pickle.loads(data)
        return {"restored": str(user_obj)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Restore failed: {e}")

@app.get("/config/secrets")
async def get_secrets():
    """
    CRITICAL VULNERABILITY: Hardcoded Credentials Leak
    Directly returns production connection strings and cleartext passwords.
    """
    return {
        "db_connection": PRODUCTION_DB_URL,
        "admin_creds": ACCOUNTS["admin"]["password"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
