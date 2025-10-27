from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import sqlite3
import os
from pathlib import Path

# ========================
# CONFIG  
# ========================
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")  # Should match auth server
JWT_ALGORITHM = "HS256"
DB_PATH = Path(__file__).parent / "data.db"

app = FastAPI(title="Resource Server - Protected API")
auth_scheme = HTTPBearer()

# ========================
# DATABASE SETUP
# ========================
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                owner TEXT NOT NULL,
                access_level TEXT NOT NULL DEFAULT 'public',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add sample data with different access levels
        cur.execute("SELECT COUNT(*) FROM items")
        if cur.fetchone()[0] == 0:
            sample_data = [
                # PUBLIC LEVEL - Everyone can see (4 items)
                ("Welcome Message", "Welcome to our platform! This is visible to everyone.", "system", "public"),
                ("Company News", "Latest company updates and announcements", "system", "public"),
                ("Public Events", "Upcoming public events and webinars", "system", "public"),
                ("Contact Info", "Public contact information and office hours", "system", "public"),
                
                # USER LEVEL - Registered users and above (6 items)
                ("Team Calendar", "Internal team calendar and schedules", "system", "user"),
                ("Project Updates", "Current project status and milestones", "system", "user"),
                ("Employee Resources", "HR resources and employee handbook", "system", "user"),
                ("Internal Tools", "Links to internal development tools", "system", "user"),
                ("Training Materials", "Employee training and onboarding docs", "system", "user"),
                ("Team Chat Logs", "Important discussions and meeting notes", "system", "user"),
                
                # ADMIN LEVEL - Admins and above (5 items)
                ("Server Configs", "Production server configuration details", "system", "admin"),
                ("User Management", "User account management and permissions", "system", "admin"),
                ("Database Backups", "Database backup schedules and procedures", "system", "admin"),
                ("API Keys", "Third-party API keys and integration details", "system", "admin"),
                ("System Monitoring", "Server monitoring and alert configurations", "system", "admin"),
                
                # SUPER_ADMIN LEVEL - Only super admins (3 items)
                ("Security Audit", "Confidential security audit results", "system", "super_admin"),
                ("Financial Reports", "Sensitive financial data and reports", "system", "super_admin"),
                ("Executive Decisions", "Board meeting minutes and strategic plans", "system", "super_admin")
            ]
            cur.executemany("INSERT INTO items (title, description, owner, access_level) VALUES (?, ?, ?, ?)", sample_data)
        conn.commit()

init_db()

# ========================
# RBAC CONFIG
# ========================
ROLE_HIERARCHY = {
    "guest": 0,
    "user": 1, 
    "admin": 2,
    "super_admin": 3
}

ACCESS_LEVELS = {
    "public": 0,     # Everyone can see
    "user": 1,       # Registered users and above
    "admin": 2,      # Admins and above
    "super_admin": 3 # Only super admins
}

def get_user_role(payload: dict) -> str:
    """Extract role from JWT payload, default to 'guest'"""
    return payload.get("role", "guest")

def can_access(user_role: str, required_level: str) -> bool:
    """Check if user role can access the required level"""
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level_num = ACCESS_LEVELS.get(required_level, 0)
    return user_level >= required_level_num

# ========================
# MODELS
# ========================
class CreateItem(BaseModel):
    title: str
    description: str = ""
    access_level: str = "public"  # public, user, admin, super_admin

# ========================
# DEPENDENCY: Verify token
# ========================
def verify_token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> dict:
    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"verify_aud": False}
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ========================
# ROUTES
# ========================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items")
def get_items(payload: dict = Depends(verify_token)):
    """Get items based on user's role and access level"""
    username = payload.get("sub", "anonymous")
    user_role = get_user_role(payload)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM items ORDER BY created_at DESC")
        all_items = [dict(row) for row in cur.fetchall()]
    
    # Filter items based on user's access level
    accessible_items = []
    for item in all_items:
        if can_access(user_role, item["access_level"]):
            accessible_items.append(item)
    
    return {
        "user": username, 
        "role": user_role,
        "items": accessible_items,
        "total_accessible": len(accessible_items),
        "total_items": len(all_items)
    }

@app.post("/items")
def create_item(item: CreateItem, payload: dict = Depends(verify_token)):
    """Create a new item with access level"""
    username = payload.get("sub", "anonymous")
    user_role = get_user_role(payload)
    
    # Validate access level
    if item.access_level not in ACCESS_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid access level")
    
    # Check if user can create items with this access level
    if not can_access(user_role, item.access_level):
        raise HTTPException(
            status_code=403, 
            detail=f"Insufficient permissions to create {item.access_level} items"
        )
    
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (title, description, owner, access_level) VALUES (?, ?, ?, ?)",
            (item.title, item.description, username, item.access_level)
        )
        item_id = cur.lastrowid
        conn.commit()
    
    return {
        "message": "Item created", 
        "id": item_id, 
        "owner": username,
        "access_level": item.access_level
    }

@app.get("/profile")
def get_profile(payload: dict = Depends(verify_token)):
    return {"username": payload.get("sub"), "message": "This is your profile"}
