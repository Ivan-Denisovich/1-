class UsernameTaken(Exception):
    """Raises if username is already taken to provide uniqueness."""


class InvalidCredentials(Exception): ...


class UserNotFound(Exception): ...


class ItemAlreadySold(Exception):
    """Raises if sold item is trying to be sold again."""


class FlatNotFound(Exception): ...


class NotAnOwnerError(Exception):
    """Raises if user that is not an owner of the property trying to sell one."""
