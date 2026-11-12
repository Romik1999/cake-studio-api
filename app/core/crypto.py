from cryptography.fernet import Fernet

from app.config import get_settings

_cipher: Fernet | None = None


def _get_cipher() -> Fernet:
    global _cipher
    if _cipher is None:
        _cipher = Fernet(get_settings().ENCRYPTION_KEY.encode())
    return _cipher


def encrypt_token(token: str) -> str:
    return _get_cipher().encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    return _get_cipher().decrypt(encrypted_token.encode()).decode()