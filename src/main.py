import streamlit as st

import ui.pages.account as account_page
import ui.pages.auth as auth_page
import ui.pages.home as home_page
from infrastructure.db import LocalMarketDatabase, LocalUserDatabase
from infrastructure.security import Sha256Hasher


def logout():
    st.session_state.pop("user_id", None)
    st.rerun()


def main():
    st.session_state.user_repo = LocalUserDatabase()
    st.session_state.market_repo = LocalMarketDatabase()
    st.session_state.hasher = Sha256Hasher()

    if "user_id" not in st.session_state:
        pages = [
            st.Page(
                auth_page.render,
                url_path="login",
                title="Авторизация",
                icon=":material/login:",
            )
        ]
    else:
        pages = {
            "": [
                st.Page(
                    home_page.render,
                    url_path="home",
                    title="Главная",
                    icon=":material/home:",
                ),
                st.Page(
                    account_page.render,
                    url_path="me",
                    title="Личный кабинет",
                    icon=":material/account_circle:",
                ),
                st.Page(
                    logout,
                    url_path="logout",
                    title="Выйти",
                    icon=":material/logout:",
                ),
            ],
        }

    pages = st.navigation(pages)
    pages.run()


if __name__ == "__main__":
    main()
