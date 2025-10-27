# JWT Authentication System with Role-Based Access Control (RBAC)

A simple, enterprise-level authentication system built with FastAPI, featuring JWT tokens and role-based access control. Perfect for learning and tutorial purposes.

## 🏗️ Architecture

This system consists of two separate servers:

1. **Auth Server** (`auth_server.py`) - Handles user registration and login, issues JWT tokens
2. **Resource Server** (`resource_server.py`) - Protected API that validates JWT tokens and serves data based on user roles

### System Flow Diagram:

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Client    │    │   Auth Server   │    │ Resource Server  │
│ (Postman/   │    │   Port: 8000    │    │   Port: 8001     │
│  Browser)   │    │                 │    │                  │
└─────────────┘    └─────────────────┘    └──────────────────┘
      │                      │                       │
      │ 1. Register/Login    │                       │
      │─────────────────────▶│                       │
      │                      │                       │
      │ 2. JWT Token         │                       │
      │◀─────────────────────│                       │
      │                      │                       │
      │ 3. API Request + JWT Token                   │
      │─────────────────────────────────────────────▶│
      │                      │                       │
      │                      │ 4. Validate JWT       │
      │                      │◀──────────────────────│
      │                      │                       │
      │                      │ 5. JWT Valid + Role   │
      │                      │──────────────────────▶│
      │                      │                       │
      │ 6. Filtered Data (based on role)             │
      │◀─────────────────────────────────────────────│
      │                      │                       │

┌─────────────────────────────────────────────────────────────────┐
│                     Databases                                   │
│                                                                 │
│  ┌─────────────┐              ┌─────────────────────────────┐   │
│  │  users.db   │              │         data.db             │   │
│  │ ┌─────────┐ │              │ ┌─────────────────────────┐ │   │
│  │ │username │ │              │ │title, description       │ │   │
│  │ │password │ │              │ │access_level (public,    │ │   │
│  │ │role     │ │              │ │user, admin, super_admin)│ │   │
│  │ └─────────┘ │              │ │owner, created_at        │ │   │
│  └─────────────┘              │ └─────────────────────────┘ │   │
└─────────────────────────────────────────────────────────────────┘
```

### Authentication Flow:
1. **Register/Login**: Client sends credentials to Auth Server
2. **JWT Token**: Auth Server validates credentials and returns JWT with role
3. **API Request**: Client uses JWT token to access Resource Server
4. **Token Validation**: Resource Server validates JWT with Auth Server's secret
5. **Role Check**: Resource Server extracts user role from JWT
6. **Filtered Response**: Resource Server returns data based on user's access level

## 🔐 Features

- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ JWT token generation and validation
- ✅ Role-based access control (RBAC)
- ✅ SQLite database storage
- ✅ FastAPI with automatic API documentation
- ✅ Clean, simple code structure

## 👥 User Roles & Access Levels

### Available Roles:
- **`user`**: Basic registered user
- **`admin`**: Administrator with elevated privileges  
- **`super_admin`**: Highest level access

### Data Access Levels:
- **`public`**: Everyone can see (4 items)
- **`user`**: Registered users and above (6 items)
- **`admin`**: Admins and above (5 items)
- **`super_admin`**: Only super admins (3 items)

### Access Matrix:
| Role | Public | User | Admin | Super Admin | Total Items |
|------|--------|------|-------|-------------|-------------|
| Guest | ✅ | ❌ | ❌ | ❌ | 4 |
| User | ✅ | ✅ | ❌ | ❌ | 10 |
| Admin | ✅ | ✅ | ✅ | ❌ | 15 |
| Super Admin | ✅ | ✅ | ✅ | ✅ | 18 |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- uv (or pip)

### Installation
```bash
# Clone the repository
git clone <your-repo>
cd auth

# Install dependencies
uv add fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]"
```

### Running the Servers

**Terminal 1 - Auth Server:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start auth server
uvicorn auth_server:app --port 8000 --reload
```

**Terminal 2 - Resource Server:**
```bash
# Activate virtual environment  
source .venv/bin/activate

# Start resource server
uvicorn resource_server:app --port 8001 --reload
```

## 📚 API Usage

### 1. Discover Available Roles
```bash
# Get available roles and descriptions
curl http://localhost:8000/roles
```

### 2. Register Users
```bash
# Register a basic user
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "john", "password": "password123", "role": "user"}'

# Register an admin
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "jane", "password": "password123", "role": "admin"}'

# Register a super admin
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "bob", "password": "password123", "role": "super_admin"}'
```

### 3. Login and Get JWT Token
```bash
# Login as user
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "john", "password": "password123"}'

# Response will include access_token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 4. Access Protected Resources
```bash
# Get items (replace YOUR_TOKEN with actual JWT token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/items

# Create new item
curl -X POST "http://localhost:8001/items" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "My Task", "description": "Something to do", "access_level": "user"}'

# Get user profile
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8001/profile
```

## 🧪 Testing with Postman

### Setup:
1. Import the endpoints into Postman
2. Set up environment variables for tokens

### Test Flow:
1. **Register** users with different roles
2. **Login** to get JWT tokens
3. **Test access** to `/items` endpoint with different user tokens
4. **Observe** how different roles see different amounts of data

### Postman Collections:
- **Auth Server**: `http://localhost:8000`
  - GET `/` - Health check
  - GET `/roles` - Available roles
  - POST `/register` - User registration
  - POST `/login` - User login

- **Resource Server**: `http://localhost:8001`
  - GET `/health` - Health check
  - GET `/items` - Get accessible items (requires auth)
  - POST `/items` - Create new item (requires auth)
  - GET `/profile` - User profile (requires auth)

## 🗃️ Database Schema

### Users Table (users.db):
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
```

### Items Table (data.db):
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    owner TEXT NOT NULL,
    access_level TEXT NOT NULL DEFAULT 'public',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Environment Variables:
- `JWT_SECRET`: Secret key for JWT signing (default: "super-secret-key")

### Key Files:
- `auth_server.py` - Authentication and JWT issuance
- `resource_server.py` - Protected API with RBAC
- `users.db` - User accounts and credentials
- `data.db` - Protected resources with access levels

## 🎯 Learning Outcomes

This project demonstrates:
- **JWT Authentication Flow**
- **Password Hashing with bcrypt**
- **Role-Based Access Control (RBAC)**
- **API Security Best Practices**
- **FastAPI Framework Usage**
- **SQLite Database Operations**
- **Microservices Architecture**

## 🛡️ Security Features

- ✅ Password hashing with bcrypt and salt
- ✅ JWT tokens with expiration
- ✅ Role-based access control
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention with parameterized queries
- ✅ Bearer token authentication
- ✅ Proper error handling

## 📖 API Documentation

Once the servers are running, access the auto-generated documentation:

- **Auth Server Docs**: http://localhost:8000/docs
- **Resource Server Docs**: http://localhost:8001/docs

## 🤝 Contributing

This is a tutorial project. Feel free to fork and modify for your own learning!

## 📄 License

MIT License - Feel free to use this for educational purposes.