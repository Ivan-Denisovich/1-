from domain.entities import Flat, User, UserProperty
from domain.value_objects import Credentials

from .exceptions import ItemAlreadySold
from .ports import MarketDatabaseRepository, PasswordHasher, UserDatabaseRepository


class Register:
    def __init__(
        self, user_repo: UserDatabaseRepository, hasher: PasswordHasher
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher

    def execute(self, username: str, password: str) -> None:
        credentials = Credentials.create(username, password)
        credentials.check_username()
        credentials.check_password()

        password_hash = self._hasher.hash(credentials.password)
        self._user_repo.register(credentials.username, password_hash)


class Login:
    def __init__(
        self, user_repo: UserDatabaseRepository, hasher: PasswordHasher
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher

    def execute(self, username: str, password: str) -> int:
        credentials = Credentials.create(username, password)

        password_hash = self._hasher.hash(credentials.password)
        return self._user_repo.login(credentials.username, password_hash)


class GetUser:
    def __init__(self, user_repo: UserDatabaseRepository) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int) -> User:
        return self._user_repo.get_user(user_id)


class GetUserProperty:
    def __init__(self, user_repo: UserDatabaseRepository) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int) -> UserProperty:
        return self._user_repo.get_property(user_id)


class AddMoney:
    def __init__(self, user_repo: UserDatabaseRepository) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: int, amount: int) -> None:
        user = self._user_repo.get_user(user_id)
        user.deposit(amount)
        self._user_repo.add_money(user_id=user_id, amount=amount)


class EditProfile:
    def __init__(
        self, user_repo: UserDatabaseRepository, hasher: PasswordHasher
    ) -> None:
        self._user_repo = user_repo
        self._hasher = hasher

    def execute(self, user_id: int, new_username: str, new_password: str) -> None:
        user = self._user_repo.get_user(user_id)
        credentials = Credentials.create(new_username, new_password)

        if new_username:
            credentials.check_username()
        if new_password:
            credentials.check_password()

        user.change_username(credentials.username)
        new_password_hash = self._hasher.hash(credentials.password)
        self._user_repo.edit_profile(
            user_id=user_id,
            new_username=credentials.username,
            new_password_hash=new_password_hash,
        )


class GetFlatList:
    def __init__(self, market_repo: MarketDatabaseRepository) -> None:
        self._market_repo = market_repo

    def execute(self) -> list[Flat]:
        return self._market_repo.get_flat_list()


class BuyFlat:
    def __init__(
        self, user_repo: UserDatabaseRepository, market_repo: MarketDatabaseRepository
    ) -> None:
        self._user_repo = user_repo
        self._market_repo = market_repo

    def execute(self, user_id: int, flat_id: int) -> None:
        user = self._user_repo.get_user(user_id)
        flat = self._market_repo.get_flat(flat_id)

        if not flat.is_available:
            raise ItemAlreadySold(f"Flat is already sold. ID: {flat_id}")

        user.charge(flat.price)
        flat.sell()
        self._market_repo.purchase_flat(user_id=user_id, flat_id=flat_id)


class SellFlat:
    def __init__(
        self, user_repo: UserDatabaseRepository, market_repo: MarketDatabaseRepository
    ) -> None:
        self._user_repo = user_repo
        self._market_repo = market_repo

    def execute(self, user_id: int, flat_id: int) -> None:
        user = self._user_repo.get_user(user_id)
        flat = self._market_repo.get_flat(flat_id)

        user.deposit(flat.price)
        flat.free()
        self._market_repo.sell_flat(user_id=user_id, flat_id=flat_id)
