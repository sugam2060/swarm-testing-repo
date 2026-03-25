import os
import json
import sqlite3
import hashlib
import secrets
import subprocess
import html
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

# ==================== SECURE CONFIGURATION ====================
# All sensitive configurations are now loaded from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///users.db")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
STRIPE_KEY = os.getenv("STRIPE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me-in-production")

app = FastAPI(title="MegaCorp Secure Portal", debug=False)

# ==================== DATABASE INITIALIZATION ====================
# Using local SQLite for demonstration, with safe practices
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        username TEXT UNIQUE, 
        password_hash TEXT, 
        email TEXT, 
        role TEXT DEFAULT 'user', 
        ssn_encrypted TEXT
    )
""")
conn.commit()

# ==================== SECURITY HELPERS ====================
def hash_password(password: str) -> str:
    """Securely hash a password using PBKDF2 with a salt."""
    salt = secrets.token_bytes(16)
    iterations = 100000
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return f"{salt.hex()}${iterations}${pwd_hash.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against its PBKDF2 hash."""
    try:
        salt_hex, iterations, hash_hex = stored_hash.split('$')
        salt = bytes.fromhex(salt_hex)
        iterations = int(iterations)
        target_hash = bytes.fromhex(hash_hex)
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        return secrets.compare_digest(target_hash, test_hash)
    except Exception:
        return False

async def verify_admin(x_admin_token: Optional[str] = Header(None)):
    if not x_admin_token or not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(status_code=403, detail="Admin access required")

# ==================== SCHEMAS ====================
class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    ssn: str

class UserLogin(BaseModel):
    username: str
    password: str

# ==================== ENDPOINTS ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # FIXED: Sanitizing user input to prevent Reflected XSS
    search = request.query_params.get("q", "")
    safe_search = html.escape(search)
    
    return f"""
    <html>
        <body>
            <h1>Welcome to MegaCorp Secure Portal</h1>
            <p>You searched for: {safe_search}</p>
            <form><input name="q" placeholder="Search..."><button>Go</button></form>
        </body>
    </html>
    """

@app.post("/register")
async def register(user_data: UserRegister):
    # FIXED: Use parameterized queries to prevent SQL Injection
    # FIXED: Hash passwords instead of storing in plaintext
    # FIXED: PII like SSN should be handled carefully (simulated encryption here)
    
    pwd_hash = hash_password(user_data.password)
    ssn_mock_encrypted = f"ENC:{user_data.ssn[::-1]}" # Mock encryption for demonstration
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, ssn_encrypted) VALUES (?, ?, ?, ?)",
            (user_data.username, pwd_hash, user_data.email, ssn_mock_encrypted)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # FIXED: No more logging sensitive data or echoing passwords
    print(f"[REGISTER] New user registered: {user_data.username}")
    
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(login_data: UserLogin):
    # FIXED: SQL Injection prevented with parameterized query
    cursor.execute("SELECT * FROM users WHERE username = ?", (login_data.username,))
    user = cursor.fetchone()
    
    if user and verify_password(user["password_hash"], login_data.password):
        # FIXED: Only return necessary, non-sensitive user data
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/admin/run")
async def admin_run(command: str, params: List[str] = [], auth: None = Depends(verify_admin)):
    """
    FIXED: Restricted administrative execution to a whitelist of commands
    and avoided shell=True.
    """
    ALLOWED_COMMANDS = {"status": ["uptime"], "check-service": ["systemctl", "status"]}
    
    if command not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=400, detail="Command not allowed")
    
    full_cmd = ALLOWED_COMMANDS[command] + params
    try:
        proc = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
        return {"stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.CalledProcessError as e:
        return {"error": str(e), "stdout": e.stdout, "stderr": e.stderr}

@app.post("/upload")
async def upload(file: UploadFile = File(...), auth: None = Depends(verify_admin)):
    # FIXED: Path Traversal prevention using fixed directory and safe filename
    # FIXED: Added file type validation
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Use UUID for internal storage to avoid conflicts and path traversal
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, safe_filename)
    
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # FIXED: Never execute uploaded files
    return {"message": "File uploaded successfully", "id": safe_filename}

@app.get("/config")
async def get_config(auth: None = Depends(verify_admin)):
    # FIXED: Only return non-sensitive configuration keys
    return {
        "database_type": "SQLite (Safe)",
        "auth_enabled": True,
        "version": "2.0.0-SECURE"
    }

@app.get("/hash")
async def secure_hash(data: str):
    # FIXED: Using SHA-256 instead of MD5
    return {"sha256": hashlib.sha256(data.encode()).hexdigest()}

if __name__ == "__main__":
    import uvicorn
    # In production, never run with debug=True
    uvicorn.run(app, host="127.0.0.1", port=8080)
