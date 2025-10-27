# ========================
# STANDARD LIBRARY IMPORTS
# ========================
import sqlite3
import time
import os
from pathlib import Path

# ========================
# THIRD-PARTY IMPORTS
# ========================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import bcrypt  # For password hashing
from jose import jwt  # For JWT token generation

# ========================
# CONFIGURATION
# ========================
# Database setup
DB_PATH = Path(__file__).parent / "users.db"

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 3600  # 1 hour

# Available user roles
VALID_ROLES = ["user", "admin", "super_admin"]


# FastAPI app
app = FastAPI()

# Database initialization
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        conn.commit()

init_db()

# ========================
# PYDANTIC MODELS
# ========================
class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "user"  # Available roles: user, admin, super_admin

class UserLogin(BaseModel):
    username: str
    password: str

# ========================
# ROUTES
# ========================
@app.get("/")
def root():
    return {"message": "Auth Server", "available_roles": VALID_ROLES}

@app.get("/roles")
def get_available_roles():
    """Get list of available user roles"""
    return {
        "available_roles": VALID_ROLES,
        "role_descriptions": {
            "user": "Basic user access - can see public and user-level items",
            "admin": "Admin access - can see public, user, and admin-level items", 
            "super_admin": "Full access - can see all items including super admin level"
        }
    }

@app.post("/register")
def register_user(user_data: UserRegister):
    # Validate input
    if not user_data.username or not user_data.password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    # Clean username
    username = user_data.username.strip().lower()
    
    # Hash password using bcrypt directly
    password_bytes = user_data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    
    # Validate role
    if user_data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Available roles: {', '.join(VALID_ROLES)}"
        )
    
    # Insert user into database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, user_data.role)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"message": f"User '{username}' registered successfully"}


@app.post("/login")
def login(user_data: UserLogin):
    username = user_data.username.strip().lower()
    password = user_data.password.encode("utf-8")

    # Fetch user from DB
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        stored_hash, user_role = row

    # Check password using bcrypt
    if not bcrypt.checkpw(password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT with role
    now = int(time.time())
    payload = {
        "sub": username,
        "role": user_role,
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
        "scope": "read write"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": JWT_EXPIRE_SECONDS
    }
