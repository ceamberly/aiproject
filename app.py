import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from src.anomaly_detector import detect_anomalies


# =====================================
# KONFIGURASI HALAMAN
# =====================================

st.set_page_config(
    page_title="AI Anomaly Detector",
    page_icon="🤖",
    layout="wide"
)


# =====================================
# CUSTOM STYLE
# =====================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #e5e7eb;
    }

    [data-testid="stMetric"] {
        background: #151f33;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #263750;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af;
    }

    [data-testid="stMetricValue"] {
        color: #60a5fa;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)


# =====================================
# HEADER
# =====================================

st.title("🤖 AI Anomaly Detector")

st.markdown(
    '<p class="subtitle">Machine Learning Based Anomaly Detection System</p>',
    unsafe_allow_html=True
)

st.divider()


# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("⚙️ Configuration")

st.sidebar.markdown("### Model Settings")

contamination = st.sidebar.slider(
    "Expected Anomaly Ratio",
    min_value=0.01,
    max_value=0.50,
    value=0.10,
    step=0.01,
    help="Perkiraan proporsi data yang dianggap anomali."
)

st.sidebar.caption(
    "Semakin tinggi nilainya, semakin banyak data yang berpotensi ditandai anomali."
)


# =====================================
# UPLOAD DATASET
# =====================================

st.subheader("📁 Dataset")

uploaded_file = st.file_uploader(
    "Upload dataset CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        st.success("Dataset berhasil dimuat!")
    except Exception as e:
        st.error(f"Gagal membaca dataset: {e}")
        st.stop()

else:
    sample_path = Path("data/sample_data.csv")

    if sample_path.exists():
        data = pd.read_csv(sample_path)
        st.info("Menggunakan dataset percobaan bawaan.")
    else:
        st.warning("Silakan upload dataset CSV untuk memulai analisis.")
        st.stop()


# =====================================
# DATA PREVIEW
# =====================================

st.markdown("### Dataset Preview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Rows", len(data))

with col2:
    st.metric("Total Columns", len(data.columns))

st.dataframe(
    data.head(10),
    use_container_width=True
)


# =====================================
# FEATURE SELECTION
# =====================================

st.divider()

st.subheader("🧠 Model Configuration")

numeric_columns = data.select_dtypes(
    include="number"
).columns.tolist()

if not numeric_columns:
    st.error("Dataset tidak memiliki kolom numerik.")
    st.stop()

default_features = [
    col for col in numeric_columns
    if col.lower() not in ["id", "transaction_id", "no"]
]

if not default_features:
    default_features = numeric_columns

selected_features = st.multiselect(
    "Pilih kolom yang akan dianalisis AI",
    options=numeric_columns,
    default=default_features
)

if not selected_features:
    st.warning("Pilih minimal satu kolom numerik.")
    st.stop()


# =====================================
# RUN DETECTION
# =====================================

if st.button(
    "🚀 Run Anomaly Detection",
    type="primary",
    use_container_width=True
):

    try:
        with st.spinner("AI sedang menganalisis dataset..."):

            analysis_data = data[selected_features].copy()

            results = detect_anomalies(
                analysis_data,
                contamination=contamination
            )

            st.session_state["results"] = results
            st.session_state["original_data"] = data.copy()

        st.success("Analisis berhasil diselesaikan!")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat analisis: {e}")


# =====================================
# DISPLAY RESULTS
# =====================================

if "results" in st.session_state:

    results = st.session_state["results"]

    st.divider()

    st.subheader("📊 Analysis Overview")

    total_data = len(results)

    normal_count = (
        results["anomaly_status"] == "Normal"
    ).sum()

    anomaly_count = (
        results["anomaly_status"] == "Anomaly"
    ).sum()

    anomaly_percentage = (
        anomaly_count / total_data * 100
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Total Data",
        f"{total_data:,}"
    )

    metric2.metric(
        "Normal Data",
        f"{normal_count:,}"
    )

    metric3.metric(
        "Anomaly Data",
        f"{anomaly_count:,}"
    )

    metric4.metric(
        "Anomaly Percentage",
        f"{anomaly_percentage:.2f}%"
    )


    # =================================
    # CHARTS
    # =================================

    st.divider()

    st.subheader("📈 Data Visualization")

    chart1, chart2 = st.columns(2)

    with chart1:

        status_counts = (
            results["anomaly_status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Count")
        )

        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Normal vs Anomaly Distribution",
            hole=0.55,
            color="Status",
            color_discrete_map={
                "Normal": "#22c55e",
                "Anomaly": "#ef4444"
            }
        )

        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    with chart2:

        fig_hist = px.histogram(
            results,
            x="anomaly_score",
            color="anomaly_status",
            nbins=20,
            title="Anomaly Score Distribution",
            color_discrete_map={
                "Normal": "#22c55e",
                "Anomaly": "#ef4444"
            }
        )

        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1120",
            plot_bgcolor="#0b1120"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )


    # =================================
    # RESULT TABLE
    # =================================

    st.divider()

    st.subheader("🔍 Detection Results")

    filter_status = st.selectbox(
        "Filter berdasarkan status",
        ["All", "Normal", "Anomaly"]
    )

    if filter_status == "All":
        filtered_results = results

    else:
        filtered_results = results[
            results["anomaly_status"] == filter_status
        ]

    st.dataframe(
        filtered_results.style.format({
            "anomaly_score": "{:.5f}"
        }),
        use_container_width=True
    )


    # =================================
    # DOWNLOAD RESULTS
    # =================================

    st.divider()

    csv_data = results.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Analysis Results",
        data=csv_data,
        file_name="anomaly_detection_results.csv",
        mime="text/csv",
        use_container_width=True
    )


# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "AI Anomaly Detector | Powered by Python & Scikit-learn"
)