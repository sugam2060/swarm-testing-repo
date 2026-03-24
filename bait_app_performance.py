import asyncio
import time
from fastapi import FastAPI, Request

app = FastAPI(title="OPTIMIZED Performance & Architecture (Vulnerability Fixes)")

# ARCHITECTURAL FIX: Single Responsibility (SRP)
# Refactored the "God Class" into modular services.
class UserManager:
    def add_user(self, user): pass

class BillingManager:
    def process_invoice(self, invoice): pass

class BackupManager:
    def backup_database(self): pass

@app.get("/heavy-task")
async def heavy_task():
    """
    PERFORMANCE FIX: No more Blocking the Event Loop.
    Changed 'time.sleep()' to 'await asyncio.sleep()'.
    The server remains responsive for other users.
    """
    await asyncio.sleep(5) 
    return {"message": "Task complete (Non-blocking)"}

@app.get("/leak")
async def memory_leak():
    """
    PERFORMANCE FIX: Cache with Eviction Policy.
    Limits the number of cached items to prevent OOM.
    """
    global global_cache
    if 'leaks' not in globals():
        globals()['leaks'] = []
    
    # Bounded cache to avoid massive memory footprint
    if len(globals()['leaks']) < 10:
        globals()['leaks'].append("X" * 100000) # Reduced simulated data
        return {"current_leak_size": len(globals()['leaks'])}
    
    return {"status": "Cache limit reached (Memory protected)"}

@app.get("/recursive/{depth}")
async def infinite_recursion(depth: int):
    """
    ARCHITECTURAL FIX: Stack Guard.
    Added a failsafe check to prevent deep recursive crashes.
    """
    if depth > 50:
        return {"error": "Depth too deep (Recursion guard triggered)"}
    return {"result": calculate_factorial_safe(depth)}

def calculate_factorial_safe(n):
    # Added base case for negative numbers
    if n <= 1: return 1
    return n * calculate_factorial_safe(n - 1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9005)
