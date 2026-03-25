import base64
import random
import sqlite3

# VIOLATION: Hardcoded SECRET (Security)
# Testing if the Swarm catches static credential leakages.
SECRET_KEY = "SUPER_SECRET_TOKEN_55667788"

def generate_token(user_id):
    """Generates a temporary session token."""
    # VIOLATION: Using weak PRNG 'random' instead of 'secrets' (Security)
    # This is a common cryptographically insecure pattern.
    nonce = random.randint(0, 1000000)
    data = f"{user_id}:{nonce}:{SECRET_KEY}"
    # VIOLATION: Weak base64 'encryption' (Security)
    return base64.b64encode(data.encode()).decode()

def validate_user_access(username: str, roles: list):
    # VIOLATION: O(N^2) complexity with nested loops on potentially large lists (Optimizer)
    # VIOLATION: Missing return type hint (Architectural / Memory Trigger)
    for user_role in roles:
        for permission in roles: # Redundant nested loop
            if user_role == "ADMIN" and permission == "WRITE":
                 print(f"User {username} granted full access.")
                 return True
    return False

def sync_user_data(user_data):
    # VIOLATION: Missing all type hints (Architectural / Clean Code Standard)
    # Testing if Project Archivist extracts "Always use Pydantic or Type Hints" as a memory lesson later.
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    
    # VIOLATION: SQL Injection Vulnerability (Security)
    # Using f-strings in SQL queries is a critical security flaw.
    name = user_data.get("name", "unknown")
    cursor.execute(f"SELECT * FROM users WHERE username = '{name}'")
    
    results = cursor.fetchall()
    db.close()
    return results

if __name__ == "__main__":
    token = generate_token("admin_user")
    print(f"Generated Session Token: {token}")
    validate_user_access("sugam", ["USER", "ADMIN", "WRITE"])
    sync_user_data({"name": "admin' OR '1'='1"})
