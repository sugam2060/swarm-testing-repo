import asyncio
import time
from fastapi import FastAPI, Request

app = FastAPI(title="Bait App: Performance & Architecture Nightmares")

# ARCHITECTURAL VULNERABILITY: The "God Class"
# Violates Single Responsibility Principle (SRP). 
# This class manages users, database, emails, and file processing in one place.
class SystemManager:
    def __init__(self):
        self.data = {}
    
    def add_user(self, user): pass
    def process_invoice(self, invoice): pass
    def send_global_email(self, msg): pass
    def backup_database(self): pass
    def resize_image(self, img_path): pass
    def calculate_taxes(self): pass

manager = SystemManager()

@app.get("/heavy-task")
async def heavy_task():
    """
    PERFORMANCE VULNERABILITY: Blocking the Event Loop
    Uses 'time.sleep()' instead of 'await asyncio.sleep()' in an async function.
    This will freeze the entire server for all users until the 5 seconds are up.
    """
    time.sleep(5) 
    return {"message": "Task complete (but I froze the server)"}

@app.get("/leak")
async def memory_leak():
    """
    PERFORMANCE VULNERABILITY: Unbounded Memory Growth
    Appends data to a global list without ever clearing it.
    Repeated calls will cause an Out-Of-Memory (OOM) crash.
    """
    global global_cache
    if 'leaks' not in globals():
        globals()['leaks'] = []
    
    globals()['leaks'].append("X" * 1000000) # Add 1MB every request
    return {"current_leak_size": len(globals()['leaks'])}

@app.get("/recursive/{depth}")
async def infinite_recursion(depth: int):
    """
    ARCHITECTURAL VULNERABILITY: Danger of Stack Overflow
    Simulates a recursive call that could crash the thread if depth is high.
    """
    return {"result": calculate_factorial_unsafe(depth)}

def calculate_factorial_unsafe(n):
    # Missing base case check for negative numbers or extremely large numbers
    if n == 0: return 1
    return n * calculate_factorial_unsafe(n - 1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9005)
