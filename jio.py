import os
import pickle
import sqlite3
import hashlib
import subprocess
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse

app = FastAPI(title="MegaCorp Internal Portal", debug=True)

# ==================== HARDCODED SECRETS ====================
DATABASE_URL = "postgresql://root:SuperSecret123!@prod-db.megacorp.internal:5432/users"
AWS_ACCESS_KEY = "my-aws-access-key-do-not-use"
AWS_SECRET_KEY = "my-aws-secret-key-do-not-use-in-production"
STRIPE_KEY = "my-stripe-secret-key-do-not-use"
JWT_SECRET = "mysecretkey123"
ADMIN_PASSWORD = "admin"

# ==================== INSECURE DATABASE ====================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, role TEXT DEFAULT 'user', ssn TEXT)")
conn.commit()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # CRITICAL: Reflected XSS - User input rendered directly in HTML
    search = request.query_params.get("q", "")
    return f"""
    <html>
        <body>
            <h1>Welcome to MegaCorp Portal</h1>
            <p>You searched for: {search}</p>
            <form><input name="q" placeholder="Search..."><button>Go</button></form>
        </body>
    </html>
    """

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    ssn = data.get("ssn")  # Storing SSN in plaintext!
    
    # CRITICAL: SQL Injection - String concatenation in query
    query = f"INSERT INTO users (username, password, email, ssn) VALUES ('{username}', '{password}', '{email}', '{ssn}')"
    cursor.execute(query)
    conn.commit()
    
    # CRITICAL: Logging sensitive PII data
    print(f"[REGISTER] New user: {username}, password: {password}, SSN: {ssn}")
    
    return {"message": "User registered", "password_echo": password}  # Echoing password back!

@app.get("/login")
async def login(username: str, password: str):
    # CRITICAL: SQL Injection in login
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        # CRITICAL: Returning ALL user data including SSN
        return {"id": user[0], "username": user[1], "password": user[2], "email": user[3], "role": user[4], "ssn": user[5]}
    return {"error": "Invalid credentials"}

@app.get("/admin/exec")
async def admin_exec(cmd: str, key: str):
    # CRITICAL: Remote Code Execution via os.system with shell=True equivalent
    if key != ADMIN_PASSWORD:
        return {"error": "Wrong key"}
    
    # DEADLY: Direct shell command execution from user input
    result = os.popen(cmd).read()
    return {"output": result}

@app.post("/admin/run")
async def admin_run(request: Request):
    data = await request.json()
    # CRITICAL: subprocess with shell=True
    proc = subprocess.Popen(data.get("command"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return {"stdout": stdout.decode(), "stderr": stderr.decode()}

@app.get("/users/export")
async def export_users():
    # CRITICAL: No authentication, dumps entire user table including SSNs and passwords
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return {"users": [{"id": u[0], "username": u[1], "password": u[2], "email": u[3], "ssn": u[5]} for u in users]}

@app.post("/deserialize")
async def deserialize(request: Request):
    # CRITICAL: Insecure deserialization - Remote Code Execution via pickle
    body = await request.body()
    obj = pickle.loads(body)  # NEVER do this with untrusted input
    return {"result": str(obj)}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # CRITICAL: Path Traversal + No file type validation
    # An attacker can upload ../../etc/cron.d/malicious_job
    filepath = f"/tmp/uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # CRITICAL: If it's a .py file, execute it immediately (!!!)
    if file.filename.endswith(".py"):
        exec(open(filepath).read())
    
    return {"saved_to": filepath}

@app.get("/config")
async def get_config():
    # CRITICAL: Leaking all secrets and environment variables
    return {
        "database_url": DATABASE_URL,
        "aws_key": AWS_ACCESS_KEY,
        "aws_secret": AWS_SECRET_KEY,
        "stripe_key": STRIPE_KEY,
        "jwt_secret": JWT_SECRET,
        "admin_password": ADMIN_PASSWORD,
        "env": dict(os.environ)
    }

@app.get("/eval")
async def eval_code(code: str):
    # CRITICAL: Direct eval() of user input
    return {"result": eval(code)}

@app.get("/hash")
async def weak_hash(data: str):
    # VULNERABILITY: Using MD5 for hashing (cryptographically broken)
    return {"md5": hashlib.md5(data.encode()).hexdigest()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
