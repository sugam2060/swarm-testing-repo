import os
import time
import base64
import hashlib
import sqlite3
import hmac
import subprocess
from typing import List, Dict, Optional

# ============================================================================
# PART 1: ARCHITECTURAL IMPROVEMENT (Dependency Injection / Config)
# ============================================================================
class SystemConfig:
    """
    Fixed: Moved from global mutable state to a proper configuration object.
    In a real app, these should be loaded from environment variables or a config file.
    """
    def __init__(self, registry: Optional[Dict[str, str]] = None):
        self._registry = registry or {
            "auth_service": os.getenv("AUTH_SERVICE_URL", "http://auth.internal"),
            "payment_gateway": os.getenv("PAYMENT_GATEWAY_URL", "http://payments.internal"),
            "user_db": os.getenv("USER_DB_NAME", "prod_users_v1")
        }

    def get_service_url(self, name: str) -> Optional[str]:
        return self._registry.get(name)

# ============================================================================
# PART 2: PERFORMANCE & OPTIMIZATION (Efficient Processor)
# ============================================================================
class OrderStatistics:
    def __init__(self, orders: List[int]):
        self.orders = orders

    def find_duplicates(self) -> List[int]:
        """
        FIXED: Optimized to O(N) complexity using a set for tracking.
        """
        seen = set()
        dupes = set()
        for order in self.orders:
            if order in seen:
                dupes.add(order)
            else:
                seen.add(order)
        return list(dupes)

# ============================================================================
# PART 3: SECURITY & VULNERABILITIES (Hardened API)
# ============================================================================
class CloudSyncService:
    """
    FIXED: Removed hardcoded secrets and command injection vulnerabilities.
    """
    def __init__(self, sync_key: Optional[str] = None):
        # Use provided key or fetch from environment
        self.remote_sync_key = sync_key or os.getenv("REMOTE_SYNC_KEY")

    def sync_to_cloud(self, bucket_name: str, local_path: str):
        """
        FIXED: Use subprocess.run with arguments list to prevent shell injection.
        Input validation should also be performed on bucket_name.
        """
        if not bucket_name.isalnum() and '-' not in bucket_name:
             raise ValueError("Invalid bucket name")
             
        command = ["aws", "s3", "sync", local_path, f"s3://{bucket_name}", "--token", self.remote_sync_key]
        # subprocess.run handles argument escaping properly.
        subprocess.run(command, check=True)

    def secure_auth_check(self, user_token: str, stored_hash: str):
        """
        FIXED: Use SHA-256 and constant-time comparison to prevent timing attacks.
        """
        provided_hash = hashlib.sha256(user_token.encode()).hexdigest()
        # hmac.compare_digest is resistant to timing attacks
        return hmac.compare_digest(provided_hash, stored_hash)

# ============================================================================
# PART 4: SOLID COMPLIANCE (Single Responsibility Separation)
# ============================================================================

class InventoryRepository:
    """Handles database interactions."""
    def __init__(self, db_path: str = ":memory:"):
        self.db = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.db.execute("CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, count INTEGER)")

    def update_stock(self, item_id: int, qty: int):
        # FIXED: Used parameterized query to prevent SQL Injection
        self.db.execute("UPDATE stock SET count = ? WHERE id = ?", (qty, item_id))
        self.db.commit()

class EmailService:
    """Handles email notifications."""
    def send_low_stock_email(self, recipient: str):
        # In a real app, use an e-mail library / SMTP config
        print(f"Sending email to {recipient} via configured SMTP...")

class Logger:
    """Handles logging and log rotation."""
    def rotate_logs(self):
        print("Rotating logs...")

class InventoryManager:
    """Orchestrates inventory operations by delegating to specialized services."""
    def __init__(self, repo: InventoryRepository, mailer: EmailService, logger: Logger):
        self.repo = repo
        self.mailer = mailer
        self.logger = logger

    def process_stock_update(self, item_id: int, qty: int, recipient: str):
        self.repo.update_stock(item_id, qty)
        if qty < 10:
            self.mailer.send_low_stock_email(recipient)
        self.logger.rotate_logs()

# ============================================================================
# MAIN ENTRY
# ============================================================================
if __name__ == "__main__":
    # Performance check
    stats = OrderStatistics([i for i in range(1000)] + [500, 500, 600])
    print(f"Duplicates found (O(N)): {stats.find_duplicates()}")
    
    # Security check (demonstration)
    # config = SystemConfig()
    # print(f"Auth URL: {config.get_service_url('auth_service')}")
    
    # Inventory check
    repo = InventoryRepository()
    mailer = EmailService()
    logger = Logger()
    manager = InventoryManager(repo, mailer, logger)
    manager.process_stock_update(1, 5, "admin@example.com")
