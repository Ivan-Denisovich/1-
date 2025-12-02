import os
import time

import streamlit as st

from application.ports import MarketDatabaseRepository, UserDatabaseRepository
from application.use_cases import BuyFlat, GetFlatList
from domain.entities import Flat
from domain.exceptions import NotEnoughMoney

from ..components.streamlit_elements import confirm_button


def display_filters(flats: list[Flat]) -> list[Flat]:
    """Filters cards by several custom parameters.

    :param flats: List of the flats to be filtered.
    :type flats: list[Flat]
    :return: Filtered flat list.
    :rtype: list[Flat]
    """
    col1, col2 = st.columns(2)

    room_options = ["Все"]
    if flats:
        least_rooms_flat = min(flats, key=lambda flat: flat.room_amount)
        most_rooms_flat = max(flats, key=lambda flat: flat.room_amount)
        min_rooms = least_rooms_flat.room_amount
        max_rooms = most_rooms_flat.room_amount
        room_options += [n for n in range(min_rooms, max_rooms + 1)]
    room_amount = col1.selectbox("Количество комнат", options=room_options)
    flats = [
        flat
        for flat in flats
        if room_amount == "Все" or flat.room_amount == room_amount
    ]

    if col2.checkbox("Только квартиры в наличии"):
        flats = [flat for flat in flats if flat.is_available]

    min_price = 0
    max_price = 100_000_000
    if flats:
        cheapest_flat = min(flats, key=lambda flat: flat.price)
        most_expensive_flat = max(flats, key=lambda flat: flat.price)
        min_price = cheapest_flat.price
        max_price = max(most_expensive_flat.price, min_price + 1)
    price_range = st.slider(
        "Цена",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=500_000,
        disabled=not flats,
    )
    flats = [
        flat
        for flat in flats
        if flat.price in range(price_range[0], price_range[1] + 1)
    ]

    return flats


def buy_flat(
    flat_id: int,
    user_repo: UserDatabaseRepository,
    market_repo: MarketDatabaseRepository,
) -> None:
    """Triggers flat purchase by the user.

    :param flat_id: ID of the flat to be bought.
    :type flat_id: int
    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param market_repo: Repository to provide market implementation linking.
    :type market_repo: MarketDatabaseRepository
    """
    uc = BuyFlat(user_repo=user_repo, market_repo=market_repo)
    try:
        uc.execute(user_id=st.session_state.user_id, flat_id=flat_id)
    except NotEnoughMoney:
        st.toast("На балансе недостаточно средств")
        time.sleep(1)
        st.rerun()
    except Exception:
        st.toast("Произошла непредвиденная ошибка, попробуйте позже")
        time.sleep(1)
        st.rerun()

    st.toast("Оплата прошла успешно")
    time.sleep(1)
    st.rerun()


@st.fragment
def display_flat_cards(
    user_repo: UserDatabaseRepository, market_repo: MarketDatabaseRepository
) -> None:
    """Displays flat cards on the main page.

    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param market_repo: Repository to provide market implementation linking.
    :type market_repo: MarketDatabaseRepository
    """
    uc = GetFlatList(market_repo)
    try:
        flats = uc.execute()
    except Exception:
        st.error("Произошла непредвиденная ошибка, попробуйте позже")
        return

    flats = display_filters(flats)
    flats.sort(key=lambda flat: flat.price)
    st.divider()

    if not flats:
        st.info("По вашему запросу ничего не найдено")
        return

    column_amount = 2
    columns = st.columns(column_amount)
    for i, flat in enumerate(flats):
        with columns[i % column_amount].container(height=400, border=True):
            title = f"{flat.address}, кв. {flat.number}"
            display_text = title if len(title) <= 18 else f"{title:.18}..."
            st.markdown(f"#### {display_text}", help=title)

            card_image_path = f"ui/assets/flat_images/{flat.id}.jpg"
            placeholder_image_path = "ui/assets/image_placeholder.jpg"
            image_path = (
                card_image_path
                if os.path.exists(card_image_path)
                else placeholder_image_path
            )
            st.image(image_path, width="stretch")

            st.write(f"Количество комнат: {flat.room_amount}")
            st.markdown(f"#### {flat.price:,} ₽".replace(",", " "))

            confirm_button_wrapper = confirm_button(
                label="Купить" if flat.is_available else "Продано",
                button_type="primary",
                key=f"buy_button{i}",
                use_container_width=True,
                disabled=not flat.is_available,
            )
            confirm_button_function = confirm_button_wrapper(buy_flat)
            confirm_button_function(
                flat_id=flat.id, user_repo=user_repo, market_repo=market_repo
            )


def render() -> None:
    """Main function of the page.  Renders all its content."""
    st.title("Квартиры")
    display_flat_cards(
        user_repo=st.session_state.user_repo, market_repo=st.session_state.market_repo
    )
