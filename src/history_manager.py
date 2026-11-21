import streamlit as st
from datetime import datetime
from src.supabase_client import get_supabase_client


def save_history(results, source_name, contamination, user_id=None):

    normal_count = int(
        (results["anomaly_status"] == "Normal").sum()
    )

    anomaly_count = int(
        (results["anomaly_status"] == "Anomaly").sum()
    )

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source_name,
        "contamination": float(contamination),
        "total_data": len(results),
        "normal": normal_count,
        "anomaly": anomaly_count
    }

    # Jika pengguna login, simpan ke Supabase
    if user_id:

        supabase = get_supabase_client()

        data = {
            "user_id": user_id,
            "source": source_name,
            "contamination": float(contamination),
            "total_data": len(results),
            "normal": normal_count,
            "anomaly": anomaly_count
        }

        response = supabase.table("anomaly_history").insert(
            data
        ).execute()

        return response.data

    # Jika tamu, simpan sementara di session
    if "guest_anomaly_history" not in st.session_state:
        st.session_state["guest_anomaly_history"] = []

    st.session_state["guest_anomaly_history"].append(entry)

    return entry


def load_history(user_id=None):

    # Jika pengguna login, ambil riwayat miliknya
    if user_id:

        supabase = get_supabase_client()

        response = (
            supabase.table("anomaly_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [
            {
                "timestamp": item["created_at"],
                "source": item["source"],
                "contamination": item["contamination"],
                "total_data": item["total_data"],
                "normal": item["normal"],
                "anomaly": item["anomaly"]
            }
            for item in response.data
        ]

    # Jika tamu, ambil riwayat sementara
    return st.session_state.get("guest_anomaly_history", [])