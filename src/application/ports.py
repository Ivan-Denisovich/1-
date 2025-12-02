from abc import ABC, abstractmethod

from domain.entities import Flat, User, UserProperty


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...


class UserDatabaseRepository(ABC):
    @abstractmethod
    def register(self, username: str, password_hash: str) -> None: ...

    @abstractmethod
    def login(self, username: str, password_hash: str) -> int: ...

    @abstractmethod
    def get_user(self, user_id: int) -> User: ...

    @abstractmethod
    def add_money(self, user_id: int, amount: int) -> None: ...

    @abstractmethod
    def edit_profile(
        self, user_id: int, new_username, new_password_hash: str
    ) -> None: ...

    @abstractmethod
    def get_property(self, user_id: int) -> UserProperty: ...


class MarketDatabaseRepository(ABC):
    @abstractmethod
    def get_flat_list(self) -> list[Flat]: ...

    @abstractmethod
    def get_flat(self, flat_id: int) -> Flat: ...

    @abstractmethod
    def purchase_flat(self, user_id: int, flat_id: int) -> None: ...

    @abstractmethod
    def sell_flat(self, user_id: int, flat_id: int) -> None: ...
