import os
import secrets
import sqlite3
import hmac
import hashlib
from typing import List, Dict, Optional, Any

# FIXED: Store secret in an environment variable or load it securely.
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "DEFAULT_SECURE_TOKEN_REPLACE_IN_PROD")

def generate_token(user_id: str) -> str:
    """Generates a secure session token using SHA-256 HMAC."""
    # FIXED: Using 'secrets' instead of 'random' for cryptographically secure nonces.
    nonce = secrets.token_hex(16)
    message = f"{user_id}:{nonce}".encode()
    
    # FIXED: Using HMAC-SHA256 for integrity and non-reversibility of the secret.
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    
    # Securely combine message and signature.
    return f"{nonce}.{signature}"

def validate_user_access(username: str, roles: List[str]) -> bool:
    """Checks if any of the provided roles grant administrative write access."""
    # FIXED: Complexity O(N). Removed redundant nested loop.
    # Check if 'ADMIN' and 'WRITE' are both present in the roles list.
    has_admin = "ADMIN" in roles
    has_write = "WRITE" in roles
    
    if has_admin and has_write:
        print(f"User {username} granted full access.")
        return True
    return False

def sync_user_data(user_data: Dict[str, Any]) -> List[Any]:
    """Fetches user information from database safely."""
    # FIXED: Added proper type hints for user_data and return type.
    
    # In practice, use a persistent DB connection pool.
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    
    # Initialize table if not exists for demo purposes.
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT)")
    
    # FIXED: SQL Injection Vulnerability. Using parameterized queries.
    name = user_data.get("name", "unknown")
    cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
    
    results = cursor.fetchall()
    db.close()
    return results

if __name__ == "__main__":
    # Test generation and validation
    user_id = "admin_user"
    token = generate_token(user_id)
    print(f"Generated Session Token (HMAC-SHA256): {token}")
    
    # Test access control
    roles = ["USER", "ADMIN", "WRITE"]
    is_authorized = validate_user_access("sugam", roles)
    print(f"Authorized: {is_authorized}")
    
    # Test sync data
    data = {"name": "admin' OR '1'='1"} # Malicious payload test
    results = sync_user_data(data)
    print(f"Sync results found: {len(results)}")
