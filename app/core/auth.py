import streamlit as st
from settings import settings


def verify_admin(username: str, password: str) -> bool:
    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        return False
    return (
        username == settings.ADMIN_USERNAME
        and password == settings.ADMIN_PASSWORD
    )


def require_admin_login() -> bool:
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    if st.session_state["is_admin"]:
        return True

    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if verify_admin(username, password):
                st.session_state["is_admin"] = True
                st.success("Logged in as admin.")
                return True
            else:
                st.error("Invalid username or password.")

    return False
