import streamlit as st
from utils.config import RAW_FILES, BRONZE_PATH, SILVER_PATH, GOLD_PATH, AMOUNT_TOLERANCE_PCT

st.set_page_config(page_title="Data Drift Trust Platform", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f7efe8 0%, #efe2d2 50%, #e7d5bf 100%);
        color: #5b4333;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #634631;
        letter-spacing: 0.2px;
    }
    .stMetric, .stAlert, .stSuccess, .stInfo {
        background: rgba(255, 249, 243, 0.8);
        border: 1px solid rgba(99, 70, 49, 0.14);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(99, 70, 49, 0.06);
        padding: 10px;
    }
    .stButton>button {
        background: #9b7a5b;
        color: white;
        border-radius: 999px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("☕ Data Quality Monitoring Dashboard")
st.write("A soft, cozy view of the CRM, Billing, and Analytics data checks for your project. 🌿")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📁 Raw files", len(RAW_FILES))
col2.metric("🧺 Bronze path", BRONZE_PATH)
col3.metric("🌊 Silver path", SILVER_PATH)
col4.metric("⚖️ Tolerance", f"{AMOUNT_TOLERANCE_PCT * 100:.0f}%")

st.subheader("What this project checks")
st.markdown(
    "- 📌 Missing records\n"
    "- 🔁 Duplicate entries\n"
    "- ⚠️ Value mismatches\n"
    "- 🌦️ Data drift over time\n"
    "- ⭐ Trust score calculation"
)

st.subheader("System overview")
st.info("The backend scripts in this folder perform the quality checks. This Streamlit page gives a simple browser-based view of the project. ☕")

st.subheader("Detected data sources")
for name, path in RAW_FILES.items():
    st.write(f"- {name}: {path}")

st.caption("Project output view")
