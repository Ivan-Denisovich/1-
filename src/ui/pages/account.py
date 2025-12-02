import os
import time

import streamlit as st

from application.exceptions import UsernameTaken
from application.ports import (
    MarketDatabaseRepository,
    PasswordHasher,
    UserDatabaseRepository,
)
from application.use_cases import GetUser, GetUserProperty, SellFlat
from domain.exceptions import InvalidPassword, InvalidUsername

from ..components.streamlit_elements import confirm_button


@st.dialog(title="Пополнить баланс")
def display_add_money_popup(user_repo: UserDatabaseRepository):
    amount = st.number_input("Введите сумму", min_value=0, step=10_000)

    col1, _ = st.columns(2)
    if col1.button(
        "Пополнить", type="primary", use_container_width=True, disabled=amount == 0
    ):
        uc = AddMoney(user_repo=user_repo)

        try:
            uc.execute(user_id=st.session_state.user_id, amount=amount)
        except Exception:
            st.error("Произошла непредвиденная ошибка, попробуйте позже")
            return

        st.success("Баланс успешно пополнен")
        time.sleep(1)
        st.rerun()


@st.dialog(title="Редактировать профиль")
def display_edit_profile_popup(
    user_repo: UserDatabaseRepository, hasher: PasswordHasher
):
    new_username = st.text_input("Новый логин (если не меняется, оставьте пустым)")
    new_password = st.text_input(
        "Новый пароль (если не меняется, оставьте пустым)", type="password"
    )
    st.caption(
        "От 8 до 20 символов, может содержать только буквы латинского алфавита, цифры и символы из набора !@#$%^&*()_+-="
    )

    col1, _ = st.columns(2)
    if col1.button(
        "Сохранить",
        type="primary",
        disabled=not new_username and not new_password,
        use_container_width=True,
    ):
        uc = EditProfile(user_repo=user_repo, hasher=hasher)
        try:
            uc.execute(
                user_id=st.session_state.user_id,
                new_username=new_username,
                new_password=new_password,
            )
        except InvalidUsername:
            st.error(
                "Имя пользователя может содержать только буквы латинского алфавита и цифры"
            )
            return
        except InvalidPassword:
            st.error("Введенный пароль не соответствует формату")
            return
        except UsernameTaken:
            st.error("Имя пользователя уже используется")
            return
        except Exception:
            st.error("Произошла непредвиденная ошибка, попробуйте позже")
            return

        st.success("Профиль успешно обновлен")
        time.sleep(1)
        st.rerun()


@st.fragment
def display_user_info(
    user_repo: UserDatabaseRepository, hasher: PasswordHasher
) -> None:
    """Displays users personal information.

    :param user_repo: Repository to provide user implementations linking.
    :type user_repo: UserDatabaseRepository
    """
    uc = GetUser(user_repo=user_repo)
    user = uc.execute(st.session_state.user_id)

    st.title("Личный кабинет")

    col1, _, col3 = st.columns([3, 1, 3])
    with col1:
        st.image("ui/assets/user.jpg", width="stretch")
        if st.button("Редактировать профиль", use_container_width=True):
            display_edit_profile_popup(user_repo=user_repo, hasher=hasher)
    with col3:
        st.subheader(f"Логин: {user.username}")
        st.subheader(f"Баланс: {user.balance:,} ₽".replace(",", " "))
        if st.button("Пополнить баланс", type="primary", use_container_width=True):
            display_add_money_popup(user_repo=user_repo)


def sell_flat(
    flat_id: int,
    user_repo: UserDatabaseRepository,
    market_repo: MarketDatabaseRepository,
) -> None:
    """Triggers flat selling.

    :param flat_id: ID of the flat to be sold.
    :type flat_id: int
    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param market_repo: Repository to provide market implementation linking.
    :type market_repo: MarketDatabaseRepository
    """
    uc = SellFlat(user_repo=user_repo, market_repo=market_repo)
    try:
        uc.execute(user_id=st.session_state.user_id, flat_id=flat_id)
    except Exception:
        st.toast("Произошла непредвиденная ошибка, попробуйте позже")
        time.sleep(1)
        st.rerun()

    st.toast("Квартира успешно продана")
    time.sleep(1)
    st.rerun()


@st.fragment
def display_user_property(
    user_repo: UserDatabaseRepository, market_repo: MarketDatabaseRepository
) -> None:
    """Displays information about users property.

    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param market_repo: Repository to provide market implementation linking.
    :type market_repo: MarketDatabaseRepository
    """
    uc = GetUserProperty(user_repo=user_repo)
    user_property = uc.execute(st.session_state.user_id)

    if not user_property.properties:
        st.info("Пока вы ничего не приобрели. Самое время купить квартиру!")
        return

    column_amount = 2
    columns = st.columns(column_amount)
    for i, flat in enumerate(user_property.properties):
        with columns[i % column_amount].container(height=400, border=True):
            title_text = f"{flat.address}, кв. {flat.number}"
            if len(title_text) > 19:
                display_text = f"{title_text[:19]}..."
            else:
                display_text = title_text
            st.markdown(f"#### {display_text}", help=title_text)

            image_path = f"ui/assets/flat_images/{flat.id}.jpg"
            if os.path.exists(image_path):
                st.image(image_path, width="stretch")
            else:
                st.image("ui/assets/image_placeholder.jpg", width="stretch")

            st.write(f"Количество комнат: {flat.room_amount}")
            st.markdown(f"#### {flat.price:,} ₽".replace(",", " "))

            confirm_button_wrapper = confirm_button(
                label="Продать",
                button_type="primary",
                key=f"sell_button{i}",
                use_container_width=True,
            )
            confirm_button_function = confirm_button_wrapper(sell_flat)
            confirm_button_function(
                flat_id=flat.id, user_repo=user_repo, market_repo=market_repo
            )


def render() -> None:
    """Main function of the page.  Renders all its content."""
    display_user_info(
        user_repo=st.session_state.user_repo, hasher=st.session_state.hasher
    )

    st.container(height=100, border=False)

    st.header("Ваша собственность")
    display_user_property(
        user_repo=st.session_state.user_repo, market_repo=st.session_state.market_repo
    )
