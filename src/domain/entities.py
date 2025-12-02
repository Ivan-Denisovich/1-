from dataclasses import dataclass

from .exceptions import NotEnoughMoney


@dataclass
class User:
    id: int
    username: str
    balance: int

    def deposit(self, amount: int) -> None:
        """Deposits user balance by the passed amount of money.

        :param amount: Amount of the money to be added to users balance.
        :type amount: int
        """
        self.balance += amount

    def charge(self, amount: int) -> None:
        """Charges user by the passed amount of money.

        :param amount: Amount of the money to be subtracted from users balance.
        :type amount: int
        :raises NotEnoughMoney: Raised when user tries to buy an item but does not have enough money on the account.
        """
        if self.balance < amount:
            raise NotEnoughMoney("Not enough money on the balance")

        self.balance -= amount

    def change_username(self, new_username: str) -> None:
        """Changes username

        :param new_username: New username to be applied.
        :type new_username: str
        """
        self.username = new_username


@dataclass
class Flat:
    id: int
    address: str
    number: int
    floor: int
    room_amount: int
    price: int
    is_available: bool

    def sell(self) -> None:
        """Is used to implement flat selling by locking its availability."""
        self.is_available = False

    def free(self) -> None:
        """Is used to implement flat stock return by unlocking its availability"""
        self.is_available = True


@dataclass
class UserProperty:
    """Model to implement user property ownership.  Implemented by linking user to
    the property list.
    """

    user_id: int
    properties: list[Flat]
