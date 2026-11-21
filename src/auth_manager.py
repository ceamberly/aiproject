import streamlit as st
from src.supabase_client import get_supabase_client


def register_user(email, password):
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        return {"error": str(e)}


def login_user(email, password):
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        st.session_state["user"] = {
            "id": response.user.id,
            "email": response.user.email
        }

        return response

    except Exception as e:
        return {"error": str(e)}


def logout_user():
    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.pop("user", None)
    st.session_state.pop("supabase_client", None)