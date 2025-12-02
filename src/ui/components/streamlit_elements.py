from typing import Literal

import streamlit as st


@st.dialog("Вы уверены?")
def display_confirmation_window(key: str) -> None:
    """Renders confirmation dialog window.

    :param key: Key to be passed to the streamlit components.  Must be unique.
    :type key: str
    """
    st.session_state[f"confirmed_{key}"] = False
    col1, col2 = st.columns(2)
    if col1.button("Да", use_container_width=True):
        st.session_state[f"confirmed_{key}"] = True
        st.rerun()
    elif col2.button("Нет", type="primary", use_container_width=True):
        st.rerun()


@st.fragment
def confirm_button(
    label: str,
    key: str,
    button_type: Literal["primary", "secondary", "tertiary"] = "secondary",
    use_container_width: bool = False,
    disabled: bool = False,
):
    def decorator(function):
        def wrapper(*args, **kwargs) -> None:
            if st.button(
                label,
                type=button_type,
                use_container_width=use_container_width,
                key=key,
                disabled=disabled,
            ):
                display_confirmation_window(key)

            if (
                f"confirmed_{key}" in st.session_state
                and st.session_state[f"confirmed_{key}"]
            ):
                st.session_state.pop(f"confirmed_{key}", None)
                function(*args, **kwargs)

        return wrapper

    return decorator
