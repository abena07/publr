import os
from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    key = os.environ["FIELD_ENCRYPTION_KEY"]
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
