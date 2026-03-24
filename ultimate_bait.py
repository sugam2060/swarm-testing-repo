import os
import time
import base64
import hashlib
import sqlite3
import requests
from typing import List, Dict

# ============================================================================
# PART 1: ARCHITECTURAL BLAST RADIUS (The "Jenga" Module)
# ============================================================================
# Changing this core utility will break every consumer in the "simulated" system.
class CoreSystemConfig:
    """
    CRITICAL ARCHITECTURAL FLAW: Global mutable state used as a dependency.
    Modifying 'GLOBAL_REGISTRY' is extremely high risk (Blast Radius).
    """
    GLOBAL_REGISTRY = {
        "auth_service": "http://auth.internal",
        "payment_gateway": "http://payments.internal",
        "user_db": "prod_users_v1"
    }

def get_service_url(name: str) -> str:
    # If this logic changes, the entire internal orchestration fails.
    return CoreSystemConfig.GLOBAL_REGISTRY.get(name)


# ============================================================================
# PART 2: PERFORMANCE & OPTIMIZATION (The "Slow" Processor)
# ============================================================================
class OrderStatistics:
    def __init__(self, orders: List[int]):
        self.orders = orders

    def find_duplicates(self) -> List[int]:
        """
        PERFORMANCE VULNERABILITY: O(N^2) Complexity.
        Using nested loops to find duplicates in a list instead of a Set.
        If 'orders' contains 100,000 items, this will hang the CPU.
        """
        dupes = []
        for i in range(len(self.orders)):
            for j in range(i + 1, len(self.orders)):
                if self.orders[i] == self.orders[j] and self.orders[i] not in dupes:
                    dupes.append(self.orders[i])
        return dupes


# ============================================================================
# PART 3: SECURITY & VULNERAILITIES (The "Exposed" API)
# ============================================================================
class LegacyUserSync:
    # SECURITY VULNERABILITY: Hardcoded Infrastructure Secrets
    REMOTE_SYNC_KEY = "SYNC_SECRET_77889900_AWS_FIXED"
    
    def sync_to_cloud(self, bucket_name: str, local_path: str):
        """
        SECURITY VULNERABILITY: OS Command Injection.
        Directly concatenating user-provided 'bucket_name' into a shell command.
        """
        os.system(f"aws s3 sync {local_path} s3://{bucket_name} --token {self.REMOTE_SYNC_KEY}")

    def insecure_auth_check(self, user_token: str):
        """
        SECURITY VULNERABILITY: Weak Cryptography (MD5) & Timing Attack.
        """
        target = hashlib.md5(b"admin_p@ss").hexdigest()
        provided = hashlib.md5(user_token.encode()).hexdigest()
        return target == provided # Vulnerable to timing attacks


# ============================================================================
# PART 4: SOLID VIOLATIONS (The "Everything" Manager)
# ============================================================================
class InventoryDatabaseEmailAndLoggingManager:
    """
    ARCHITECTURAL FLAW: Violation of Single Responsibility Principle (SRP).
    This class handles DB connections, Email logic, AND Log rotation.
    """
    def __init__(self):
        self.db = sqlite3.connect(":memory:")

    def update_stock(self, item_id: int, qty: int):
        self.db.execute(f"UPDATE stock SET count = {qty} WHERE id = {item_id}") # SQLi potential

    def send_low_stock_email(self, recipient: str):
        print(f"Sending email to {recipient} via SMTP...") # Hardcoded logic

    def rotate_logs(self):
        pass # Unrelated responsibility


# ============================================================================
# MAIN ENTRY (Simulated)
# ============================================================================
if __name__ == "__main__":
    # Simulate a slow process
    stats = OrderStatistics([i for i in range(1000)] + [500])
    print(f"Duplicates found: {stats.find_duplicates()}")
    
    # Simulate a dangerous sync
    syncer = LegacyUserSync()
    # Potential exploit: syncer.sync_to_cloud("; rm -rf / ;", "/tmp") 
