import hashlib

password = "mypassword1234"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)