from dataclasses import dataclass
from typing import Self

from .exceptions import InvalidPassword, InvalidUsername


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str

    @classmethod
    def create(cls, username: str, password: str) -> Self:
        return cls(username.lower(), password)

    def check_username(self) -> None:
        if not self._username_is_valid(self.username):
            raise InvalidUsername("Invalid username")

    def check_password(self) -> None:
        if not self._password_is_valid(self.password):
            raise InvalidPassword("Invalid password")

    @staticmethod
    def _username_is_valid(username: str) -> bool:
        return username.isalnum()

    @staticmethod
    def _password_is_valid(password: str) -> bool:
        SPECIAL_SYMBOLS = "!@#$%^&*()_+-="

        length_correct = 8 <= len(password) <= 20
        all_in_alphabet = all(
            symbol.isalnum() or symbol in SPECIAL_SYMBOLS for symbol in password
        )

        return length_correct and all_in_alphabet
