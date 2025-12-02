import pandas as pd

from application.exceptions import (
    FlatNotFound,
    InvalidCredentials,
    NotAnOwnerError,
    UsernameTaken,
    UserNotFound,
)
from application.ports import MarketDatabaseRepository, UserDatabaseRepository
from domain.entities import Flat, User, UserProperty
from domain.exceptions import NotEnoughMoney

USERS_LOCAL_TABLE_PATH = "data/db/users.csv"
FLATS_LOCAL_TABLE_PATH = "data/db/flats.csv"
OWNERS_LOCAL_TABLE_PATH = "data/db/owners.csv"


class LocalUserDatabase(UserDatabaseRepository):
    def register(self, username: str, password_hash: str) -> None:
        df_users = pd.read_csv(USERS_LOCAL_TABLE_PATH)

        if username in df_users["username"].values:
            raise UsernameTaken("This username is not available")

        df_new_user = pd.DataFrame(
            [
                {
                    "id": max(df_users["id"]) + 1,
                    "username": username,
                    "password_hash": password_hash,
                    "balance": 0,
                }
            ]
        )
        df_users = pd.concat([df_users, df_new_user], ignore_index=True)
        df_users.to_csv(USERS_LOCAL_TABLE_PATH, index=False)

    def login(self, username: str, password_hash: str) -> int:
        df_users = pd.read_csv(USERS_LOCAL_TABLE_PATH)
        user_data = df_users[
            (df_users["username"] == username)
            & (df_users["password_hash"] == password_hash)
        ]

        if user_data.empty:
            raise InvalidCredentials("Invalid credentials")

        user_id = user_data["id"].values[0]
        return user_id

    def get_user(self, user_id: int) -> User:
        df_users = pd.read_csv(USERS_LOCAL_TABLE_PATH)
        user_data = df_users[df_users["id"] == user_id]

        if user_data.empty:
            raise UserNotFound(f"User not found. ID: {user_id}")

        user = User(
            id=user_data["id"].values[0],
            username=user_data["username"].values[0],
            balance=user_data["balance"].values[0],
        )
        return user

    def get_property(self, user_id: int) -> UserProperty:
        df_flats = pd.read_csv(FLATS_LOCAL_TABLE_PATH)
        df_owners = pd.read_csv(OWNERS_LOCAL_TABLE_PATH)

        df_owners = df_owners[df_owners["user_id"] == user_id]
        df_owners = df_owners.join(df_flats.set_index("id"), on="flat_id")

        property_list = []
        for property_data in df_owners.to_dict(orient="records"):
            try:
                flat_id = property_data["flat_id"]
                address = property_data["address"]
                number = property_data["number"]
                floor = property_data["floor"]
                room_amount = property_data["room_amount"]
                price = property_data["price"]
            except KeyError:
                continue

            flat = Flat(
                id=flat_id,
                address=address,
                number=number,
                floor=floor,
                room_amount=room_amount,
                price=price,
                is_available=False,
            )
            property_list.append(flat)

        user_property = UserProperty(user_id, property_list)
        return user_property

    def add_money(self, user_id: int, amount: int) -> None:
        pass

    def edit_profile(self, user_id: int, new_username, new_password_hash: str) -> None:
        pass


class LocalMarketDatabase(MarketDatabaseRepository):
    def get_flat_list(self) -> list[Flat]:
        df_flats = pd.read_csv(FLATS_LOCAL_TABLE_PATH)
        df_owners = pd.read_csv(OWNERS_LOCAL_TABLE_PATH)

        sold_flat_ids = df_owners["flat_id"].tolist()
        flat_info_list = []
        for flat_data in df_flats.to_dict(orient="records"):
            try:
                flat_id = flat_data["id"]
                address = flat_data["address"]
                floor = flat_data["floor"]
                number = flat_data["number"]
                room_amount = flat_data["room_amount"]
                price = flat_data["price"]
            except KeyError:
                continue

            flat_info = Flat(
                id=flat_id,
                address=address,
                floor=floor,
                number=number,
                room_amount=room_amount,
                price=price,
                is_available=flat_id not in sold_flat_ids,
            )
            flat_info_list.append(flat_info)
        return flat_info_list

    def get_flat(self, flat_id: int) -> Flat:
        df_flats = pd.read_csv(FLATS_LOCAL_TABLE_PATH)
        df_owners = pd.read_csv(OWNERS_LOCAL_TABLE_PATH)

        flat_data = df_flats[df_flats["id"] == flat_id]
        sold_flat_ids = df_owners["flat_id"].tolist()

        try:
            flat_id = flat_data["id"].values[0]
            address = flat_data["address"].values[0]
            number = flat_data["number"].values[0]
            floor = flat_data["floor"].values[0]
            room_amount = flat_data["room_amount"].values[0]
            price = flat_data["price"].values[0]
        except KeyError:
            raise FlatNotFound(f"Flat not found. ID: {flat_id}")

        flat = Flat(
            id=flat_id,
            address=address,
            number=number,
            floor=floor,
            room_amount=room_amount,
            price=price,
            is_available=flat_id not in sold_flat_ids,
        )
        return flat

    def purchase_flat(self, user_id: int, flat_id: int) -> None:
        df_users = pd.read_csv(USERS_LOCAL_TABLE_PATH)
        df_flats = pd.read_csv(FLATS_LOCAL_TABLE_PATH)
        df_owners = pd.read_csv(OWNERS_LOCAL_TABLE_PATH)

        user_data = df_users[df_users["id"] == user_id]
        flat_data = df_flats[df_flats["id"] == flat_id]

        user_balance = user_data["balance"].values[0]
        flat_price = flat_data["price"].values[0]

        if user_balance < flat_price:
            raise NotEnoughMoney(f"User does not have enough money. ID: {user_id}")

        df_users.loc[df_users["id"] == user_id, "balance"] = user_balance - flat_price
        df_owners_new = pd.DataFrame([{"user_id": user_id, "flat_id": flat_id}])
        df_owners = pd.concat([df_owners, df_owners_new], ignore_index=True)

        df_users.to_csv(USERS_LOCAL_TABLE_PATH, index=False)
        df_owners.to_csv(OWNERS_LOCAL_TABLE_PATH, index=False)

    def sell_flat(self, user_id: int, flat_id: int) -> None:
        df_users = pd.read_csv(USERS_LOCAL_TABLE_PATH)
        df_flats = pd.read_csv(FLATS_LOCAL_TABLE_PATH)
        df_owners = pd.read_csv(OWNERS_LOCAL_TABLE_PATH)

        ownership_data = df_owners[
            (df_owners["user_id"] == user_id) & (df_owners["flat_id"] == flat_id)
        ]
        if ownership_data.empty:
            raise NotAnOwnerError("User is not the owner of the property")

        user_data = df_users[df_users["id"] == user_id]
        flat_data = df_flats[df_flats["id"] == flat_id]

        user_balance = user_data["balance"].values[0]
        flat_price = flat_data["price"].values[0]

        df_users.loc[df_users["id"] == user_id, "balance"] = user_balance + flat_price
        df_owners = df_owners[
            (df_owners["user_id"] != user_id) | (df_owners["flat_id"] != flat_id)
        ]

        df_users.to_csv(USERS_LOCAL_TABLE_PATH, index=False)
        df_owners.to_csv(OWNERS_LOCAL_TABLE_PATH, index=False)
