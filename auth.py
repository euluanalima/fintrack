import streamlit as st
from supabase import create_client


def get_supabase_settings():
    try:
        section = st.secrets["supabase"]
        return str(section["url"]), str(section["publishable_key"])
    except Exception:
        return None, None


def get_supabase_client():
    if "supabase_client" not in st.session_state:
        url, key = get_supabase_settings()
        if not url or not key:
            return None
        st.session_state.supabase_client = create_client(url, key)
    return st.session_state.supabase_client


def is_logged_in():
    return bool(st.session_state.get("user_id"))


def current_user_id():
    return st.session_state.get("user_id")


def current_user_email():
    return st.session_state.get("user_email", "")


def login(email, password):
    client = get_supabase_client()
    response = client.auth.sign_in_with_password(
        {"email": email.strip(), "password": password}
    )
    if response.user:
        st.session_state.user_id = str(response.user.id)
        st.session_state.user_email = response.user.email or email.strip()
        return True
    return False


def signup(email, password):
    client = get_supabase_client()
    response = client.auth.sign_up(
        {"email": email.strip(), "password": password}
    )
    if response.session and response.user:
        st.session_state.user_id = str(response.user.id)
        st.session_state.user_email = response.user.email or email.strip()
        return "logged_in"
    return "confirmation_required"


def logout():
    client = get_supabase_client()
    try:
        if client:
            client.auth.sign_out()
    finally:
        for key in ["user_id", "user_email", "supabase_client"]:
            st.session_state.pop(key, None)


def send_password_reset(email):
    client = get_supabase_client()
    client.auth.reset_password_for_email(email.strip())
