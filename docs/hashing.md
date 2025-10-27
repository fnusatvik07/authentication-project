# 🔐 Password Hashing and JWT Authentication Explained

## 🧩 1. Why Hashing Is Needed in JWT Auth Systems

When users sign up or log in:

* You **should never store passwords as plain text**.
* Instead, store a **hashed version** of the password in the database.
* When a user logs in, hash the entered password again and compare it with the stored hash.
* If they match → you generate a **JWT token** (JSON Web Token) to authenticate the user.

👉 JWT = used after login
👉 Hashing = protects passwords before login

---

## ⚙️ 2. What Is Hashing?

**Hashing** = one-way encryption.
Given an input string (like `"mypassword123"`), it produces a **fixed-length, irreversible** output.
Even if someone steals the hash, they **can’t reverse it** back to the password.

```python
import hashlib

password = "mypassword123"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

**Output example:**

```
ef92b778ba... (64-character hash)
```

> 🔐 SHA256, SHA512, MD5, BLAKE2 are examples of hashing algorithms.

---

## 🚫 3. Why Plain Hashing (like SHA256) Is Not Enough

Attackers can:

* Use **rainbow tables** (precomputed hashes) to guess passwords.
* Use **brute-force** attacks (try millions of passwords quickly).

✅ So we use **Salting + Slow Hashing algorithms**.

---

## 🧂 4. What Is Salting?

A **salt** is a random string added to the password before hashing.
This ensures even if two users have the same password, their hashes differ.

### Example using `crypt`

```python
import crypt
import os

# Generate a random salt
salt = crypt.mksalt(crypt.METHOD_SHA512)

password = "mypassword123"
hashed = crypt.crypt(password, salt)

print("Salt:", salt)
print("Hashed password:", hashed)
```

**Output example:**

```
Salt: $6$Ft8dc7j2xC$  
Hashed password: $6$Ft8dc7j2xC$h7tqX9Vh...etc
```

---

## 🧱 5. More Secure Hashing Algorithms for Passwords

| Method     | Library                 | Description                                                   |
| ---------- | ----------------------- | ------------------------------------------------------------- |
| **bcrypt** | `bcrypt`                | Adds salt internally and is slow enough to resist brute-force |
| **scrypt** | `hashlib.scrypt()`      | Memory-hard algorithm — great for security                    |
| **argon2** | `argon2-cffi`           | Winner of the Password Hashing Competition (PHC)              |
| **pbkdf2** | `hashlib.pbkdf2_hmac()` | NIST-approved and widely used in production                   |

---

## 🔐 6. Example: Using `bcrypt`

```python
import bcrypt

# Hashing
password = b"mypassword123"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print("Hashed:", hashed)

# Verifying
entered_password = b"mypassword123"
if bcrypt.checkpw(entered_password, hashed):
    print("✅ Password match")
else:
    print("❌ Wrong password")
```

---

## 💾 7. Example: Using PBKDF2

```python
import hashlib, os, binascii

password = b"mypassword123"
salt = os.urandom(16)

key = hashlib.pbkdf2_hmac(
    'sha256',  # Hash algorithm
    password,  # Password
    salt,      # Salt
    100000     # Iterations
)

print("Salt:", binascii.hexlify(salt))
print("Derived key:", binascii.hexlify(key))
```

---

## ⚡ 8. Example: Using Argon2 (Modern & Recommended)

Install:

```bash
pip install argon2-cffi
```

Then:

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

hashed = ph.hash("mypassword123")
print("Hashed:", hashed)

try:
    ph.verify(hashed, "mypassword123")
    print("✅ Password match")
except:
    print("❌ Wrong password")
```

---

## 🔄 9. How It Fits with JWT

Here’s a mini flow:

```python
from fastapi import FastAPI, HTTPException
from jose import jwt
import bcrypt

JWT_SECRET = "myjwtsecret"
JWT_ALGORITHM = "HS256"

app = FastAPI()

users_db = {}  # username: hashed_password

@app.post("/register")
def register(username: str, password: str):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users_db[username] = hashed_pw
    return {"message": "User registered"}

@app.post("/login")
def login(username: str, password: str):
    if username not in users_db:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_pw = users_db[username]
    if not bcrypt.checkpw(password.encode(), hashed_pw):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = jwt.encode({"user": username}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token}
```

---

## 🧠 10. Summary

| Concept          | Purpose                                 | Example                             |
| ---------------- | --------------------------------------- | ----------------------------------- |
| **Hashing**      | Convert password into irreversible form | SHA256                              |
| **Salting**      | Add randomness to hash                  | crypt / bcrypt                      |
| **Slow Hashing** | Slow down brute-force                   | bcrypt / scrypt / pbkdf2 / argon2   |
| **JWT**          | Used *after* password verification      | Encodes session info, not passwords |
