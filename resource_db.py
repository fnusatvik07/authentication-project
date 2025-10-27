# ========================
# DATABASE SETUP
# ========================

import sqlite3 
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

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