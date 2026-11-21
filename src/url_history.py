import streamlit as st
from src.supabase_client import get_supabase_client


def save_url_history(result, user_id=None):

    entry = {
        "url": result["url"],
        "domain": result["domain"],
        "risk_level": result["risk_level"],
        "risk_score": int(result["risk_score"]),
        "status": result["status"],
        "findings": result["findings"]
    }

    # Jika pengguna login, simpan ke Supabase
    if user_id:

        supabase = get_supabase_client()

        data = {
            "user_id": user_id,
            **entry
        }

        response = supabase.table("url_history").insert(
            data
        ).execute()

        return response.data

    # Jika tamu, simpan sementara di session
    if "guest_url_history" not in st.session_state:
        st.session_state["guest_url_history"] = []

    st.session_state["guest_url_history"].append(entry)

    return entry


def load_url_history(user_id=None):

    # Jika pengguna login, ambil riwayat miliknya
    if user_id:

        supabase = get_supabase_client()

        response = (
            supabase.table("url_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [
            {
                "timestamp": item["created_at"],
                "url": item["url"],
                "domain": item["domain"],
                "risk_level": item["risk_level"],
                "risk_score": item["risk_score"],
                "status": item["status"],
                "findings": item["findings"]
            }
            for item in response.data
        ]

    # Jika tamu, ambil riwayat sementara
    return st.session_state.get("guest_url_history", [])