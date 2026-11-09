import os
from cryptography.fernet import Fernet

KEY = os.getenv("ENCRYPTION_KEY")

if not KEY:
    raise ValueError("ENCRYPTION_KEY is not set in .env")

cipher = Fernet(KEY.encode())

def encrypt_token(token: str) -> str:
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    return cipher.decrypt(encrypted_token.encode()).decode()