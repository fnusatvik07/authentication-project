# 🧩 Understanding Base64 Encoding in JWT

## 1. What Is Base64 Encoding?

**Base64 encoding** is a way to represent binary or text data using only 64 printable characters.
It is **not encryption** — it’s just a **data representation technique** used to make data safe for transmission (especially over URLs or HTTP headers).

Base64 uses these characters:

```
A-Z, a-z, 0-9, +, /  (and '=' for padding)
```

Example:

```python
import base64

text = "hello world"
encoded = base64.b64encode(text.encode())
print(encoded)          # b'aGVsbG8gd29ybGQ='

# Decode back
decoded = base64.b64decode(encoded)
print(decoded.decode()) # 'hello world'
```

---

## 2. Why JWT Uses Base64

A **JWT (JSON Web Token)** is composed of **three parts**, separated by dots (`.`):

```
HEADER.PAYLOAD.SIGNATURE
```

Each of these parts is **Base64URL encoded**, meaning they’re encoded using Base64 but made **URL-safe** by replacing:

* `+` → `-`
* `/` → `_`
* Removing `=` padding

Example JWT (shortened):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  # Header
eyJ1c2VyIjoiam9obiIsImlhdCI6MTY5ODQ5ODQ3OX0.  # Payload
Ff1p7s9W9u3Xj4P6nI4D1hM3GcDbyvP5xPZVgZn1v3M   # Signature
```

---

## 3. Base64 in Each JWT Component

### 🧱 Header

Contains metadata about the token — e.g. algorithm and type.

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Encoded (Base64URL):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

### 📦 Payload

Contains the claims (data about the user):

```json
{
  "user": "john",
  "role": "admin"
}
```

Encoded (Base64URL):

```
eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiJ9
```

### ✍️ Signature

This part ensures integrity.
It’s created by hashing the header and payload with a secret key, then encoding again in Base64URL.

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

Example using Python:

```python
import base64, hmac, hashlib, json

header = {"alg": "HS256", "typ": "JWT"}
payload = {"user": "john", "role": "admin"}

# Encode parts
header_enc = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
payload_enc = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')

# Create signature
secret = b"mysecret"
message = header_enc + b'.' + payload_enc
signature = base64.urlsafe_b64encode(
    hmac.new(secret, message, hashlib.sha256).digest()
).rstrip(b'=')

jwt_token = b'.'.join([header_enc, payload_enc, signature])
print(jwt_token.decode())
```

---

## 4. Base64 vs Base64URL

| Feature       | Base64              | Base64URL           |
| ------------- | ------------------- | ------------------- |
| Character Set | A–Z, a–z, 0–9, +, / | A–Z, a–z, 0–9, -, _ |
| Padding       | Uses `=`            | Usually omitted     |
| URL-safe      | ❌ No                | ✅ Yes               |

JWT uses **Base64URL** because tokens are often sent via URLs or HTTP headers.

---

## 5. Decoding a JWT

To decode manually:

```python
import base64, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiJ9.signature"

header_b64, payload_b64, signature_b64 = token.split('.')

# Decode Base64URL
header_json = base64.urlsafe_b64decode(header_b64 + '==').decode()
payload_json = base64.urlsafe_b64decode(payload_b64 + '==').decode()

print(json.loads(header_json))
print(json.loads(payload_json))
```

---

## 6. Key Takeaways

| Concept            | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Base64**         | Represents binary/text in safe ASCII format                  |
| **Base64URL**      | URL-safe version of Base64 used in JWT                       |
| **JWT Encoding**   | Header + Payload are Base64URL encoded                       |
| **JWT Decoding**   | Base64URL decoding gives you readable JSON                   |
| **Not Encryption** | Anyone can decode Base64 — security comes from the signature |

---

## 7. Summary Diagram

```
Header (JSON)   → Base64URL Encode → eyJhbGciOi...
Payload (JSON)  → Base64URL Encode → eyJ1c2VyIj...
Signature = HMACSHA256(header.payload, secret) → Base64URL Encode

Final JWT = header.payload.signature
```

---

✅ **Remember:** Base64 = readability, not security.
The **signature** ensures trust, not the encoding.
