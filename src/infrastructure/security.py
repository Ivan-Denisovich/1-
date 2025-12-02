import hashlib

from application.ports import PasswordHasher


class Sha256Hasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
