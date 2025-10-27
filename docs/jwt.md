# 🔐 JSON Web Tokens (JWT) – Complete Explanation

## 1. What Is JWT?

**JWT (JSON Web Token)** is an open standard (RFC 7519) used for securely transmitting information between two parties — typically a **client** and a **server**.
It’s a **compact, URL-safe**, and **digitally signed** token that ensures data integrity and authenticity.

---

## 2. JWT Structure

A JWT has **three parts**, separated by dots (`.`):

```
HEADER.PAYLOAD.SIGNATURE
```

Example JWT:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiJ9.sXJ3Puw1I1V2PQ6N6rcT6gwbHCVkIlpG8yhp1H_YHjU
```

Each section is **Base64URL encoded JSON**:

1. **Header** → Metadata (algorithm, type)
2. **Payload** → Claims (data)
3. **Signature** → Proof that the token hasn’t been tampered with

---

## 3. JWT Header

Example:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

* `alg`: Algorithm used to sign the token (e.g., HS256 = HMAC-SHA256)
* `typ`: Type of token (JWT)

Encoded (Base64URL):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

---

## 4. JWT Payload

Contains user-specific information and other claims:

```json
{
  "user": "john",
  "role": "admin",
  "exp": 1710000000,
  "iat": 1709990000
}
```

Common claim fields:

| Field | Meaning                          |
| ----- | -------------------------------- |
| `iss` | Issuer of the token              |
| `sub` | Subject (user or entity)         |
| `aud` | Audience (intended recipient)    |
| `exp` | Expiration time (Unix timestamp) |
| `iat` | Issued at time                   |
| `nbf` | Not valid before                 |

Encoded (Base64URL):

```
eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMDAwMDAwMCwiaWF0IjoxNzA5OTkwMDAwfQ
```

---

## 5. JWT Signature

The signature ensures that the token’s data hasn’t been changed.

It’s generated like this:

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

Example in Python:

```python
import hmac, hashlib, base64, json

header = {"alg": "HS256", "typ": "JWT"}
payload = {"user": "john", "role": "admin"}

header_enc = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
payload_enc = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')

secret = b"mysecret"
message = header_enc + b'.' + payload_enc

signature = base64.urlsafe_b64encode(
    hmac.new(secret, message, hashlib.sha256).digest()
).rstrip(b'=')

jwt_token = b'.'.join([header_enc, payload_enc, signature])
print(jwt_token.decode())
```

---

## 6. How JWT Is Created (Step-by-Step)

1. **User logs in** with username & password.
2. **Server verifies** credentials using hashed password.
3. **Server creates payload**, e.g. `{ "user": "john", "exp": 1710000000 }`
4. **Header + Payload encoded** using Base64URL.
5. **Signature generated** using secret key.
6. **JWT returned** to client (as response or cookie).

---

## 7. How JWT Is Verified

When the client sends the JWT back (in `Authorization: Bearer <token>` header):

1. Server **splits** the token → header, payload, signature.
2. Server **recomputes** the signature using header + payload + secret.
3. If computed signature == token’s signature → ✅ Valid
4. Otherwise → ❌ Invalid or Tampered
5. Server also checks expiration (`exp`) and other claims.

Example verification (using `python-jose`):

```python
from jose import jwt, JWTError

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

token = jwt.encode({"user": "john"}, SECRET_KEY, algorithm=ALGORITHM)
print(token)

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("✅ Verified:", payload)
except JWTError as e:
    print("❌ Invalid token:", e)
```

---

## 8. What Happens If Someone Changes the JWT?

Let’s say an attacker changes this part of the token:

```
Original Payload: {"user": "john", "role": "user"}
Changed Payload: {"user": "john", "role": "admin"}
```

* They can Base64URL-decode and modify it easily.
* But when they re-encode it, the **signature won’t match** anymore.
* The server will compute the new signature and detect a mismatch.

👉 The token becomes **invalid**, and the server rejects it.

---

## 9. JWT Expiration & Revocation

JWTs are **stateless**, meaning the server doesn’t store them by default.
That’s why expiration (`exp`) is critical.

To manually invalidate tokens:

* Maintain a **denylist** of revoked tokens.
* Rotate your **secret key** (makes all previous tokens invalid).
* Set **short expiration** (e.g. 15 minutes).

---

## 10. Common Algorithms

| Algorithm | Type       | Description                           |
| --------- | ---------- | ------------------------------------- |
| `HS256`   | Symmetric  | HMAC + SHA256 using one secret key    |
| `RS256`   | Asymmetric | Uses public/private key pair          |
| `ES256`   | Asymmetric | Uses Elliptic Curve (smaller, faster) |

---

## 11. JWT in FastAPI Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

JWT_SECRET = "mysecret"
JWT_ALGORITHM = "HS256"
auth_scheme = HTTPBearer()

app = FastAPI()

@app.get("/secure")
def secure_route(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"message": "Access granted", "data": payload}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
```

---

## 12. Key Takeaways

| Concept        | Meaning                                      |
| -------------- | -------------------------------------------- |
| **JWT**        | A signed JSON-based token for authentication |
| **Header**     | Algorithm & token type                       |
| **Payload**    | User data (claims)                           |
| **Signature**  | Prevents tampering                           |
| **Base64URL**  | Encoding format used in JWT                  |
| **HS256**      | Common signing algorithm                     |
| **Tampering**  | Invalidates the signature                    |
| **Expiration** | Prevents long-term misuse                    |

---

## 13. Visual Flow

```
User Login → Server Verifies Credentials
       ↓
Server Creates JWT (Header + Payload + Signature)
       ↓
Client Stores Token (e.g. LocalStorage or Cookie)
       ↓
Client Sends Token in Request Header
       ↓
Server Verifies Signature & Expiry
       ↓
Access Granted ✅ or Denied ❌
```

---

✅ **In Summary:** JWT provides a stateless, compact, and secure way to authenticate users.
If **any bit changes** — the signature no longer matches, and the token is **immediately invalid**.
