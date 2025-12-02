import time

import streamlit as st

from application.exceptions import InvalidCredentials, UsernameTaken
from application.ports import PasswordHasher, UserDatabaseRepository
from application.use_cases import Login, Register
from domain.exceptions import InvalidPassword, InvalidUsername


@st.dialog("Регистрация")
def display_registration_popup(
    user_repo: UserDatabaseRepository, hasher: PasswordHasher
) -> None:
    """Displays registration dialog window.

    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param hasher: Repository to provide password hasher implementation linking.
    :type hasher: PasswordHasher
    """
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    st.caption(
        "От 8 до 20 символов, может содержать только буквы латинского алфавита, цифры и символы из набора !@#$%^&*()_+-="
    )
    repeated_password = st.text_input("Подтверждение пароля", type="password")

    if st.button("Зарегистрироваться", type="primary"):
        if not username or not password or not repeated_password:
            st.error("Не все поля заполнены")
            return

        if password != repeated_password:
            st.error("Введенные пароли не совпадают")
            return

        register_uc = Register(user_repo=user_repo, hasher=hasher)
        try:
            register_uc.execute(username=username, password=password)
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

        st.success("Вы успешно зарегистрировались")
        time.sleep(1)
        st.rerun()


@st.fragment
def display_login_form(
    user_repo: UserDatabaseRepository, hasher: PasswordHasher
) -> None:
    """Displays basic login form on user landing.

    :param user_repo: Repository to provide user implementation linking.
    :type user_repo: UserDatabaseRepository
    :param hasher: Repository to provide password hasher implementation linking.
    :type hasher: PasswordHasher
    """
    with st.form("login_form"):
        login_uc = Login(user_repo=user_repo, hasher=hasher)

        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")

        col1, col2, _ = st.columns([3, 3, 4])

        if col2.form_submit_button(
            "Зарегистрироваться", type="primary", use_container_width=True
        ):
            display_registration_popup(user_repo=user_repo, hasher=hasher)

        if col1.form_submit_button("Войти", use_container_width=True):
            try:
                st.session_state.user_id = login_uc.execute(
                    username=username, password=password
                )
            except InvalidCredentials:
                st.error("Неверный логин или пароль")
                return
            except Exception:
                st.error("Произошла непредвиденная ошибка, попробуйте позже")
                return

            st.toast(body="Авторизация прошла успешно")
            time.sleep(1)
            st.rerun()


def render() -> None:
    """Main function of the page.  Renders all its content."""
    st.title("Otiva")
    st.caption("Не найдется ничего")
    display_login_form(
        user_repo=st.session_state.user_repo, hasher=st.session_state.hasher
    )
