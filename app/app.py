import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from src.sqlite_io import init_db, run_query
from src.generate_data import run_data_generation
from src.build_facts_kpis import run_pipeline
from src.quality_checks import run_quality_gates
from src.config import DB_PATH
import os

st.set_page_config(
    page_title="Clinical Quality & Safety OPS",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Clinical Quality & Medication Safety Operations Dashboard")
st.markdown("**Executive Brief (Synthetic Data)** | *Not for Clinical Use*")

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.info("System Control Panel")
    if st.button("🏗️ Build / Refresh DB", type="primary"):
        with st.status("Executing Pipeline...", expanded=True) as status:
            st.write("Initializing Schema...")
            init_db()
            st.write("Generating Synthetic Data (Patients, Encounters)...")
            run_data_generation()
            st.write("Building Derived Facts & KPIs...")
            run_pipeline()
            st.write("Running Quality Gates...")
            run_quality_gates()
            status.update(label="Pipeline Completed via SQLite!", state="complete", expanded=False)
        st.success("Database rebuilt successfully.")

with col2:
    if os.path.exists(DB_PATH):
        st.success(f"Connected to DB: `{DB_PATH}`")
        try:
            counts = run_query("SELECT (SELECT Count(*) FROM patients) as p, (SELECT Count(*) FROM encounters) as e")
            st.metric("Total Patients", counts['p'].iloc[0])
            st.metric("Total Encounters", counts['e'].iloc[0])
        except Exception as e:
            st.error(f"DB Error: {e}")
    else:
        st.warning("Database not found. Click 'Build / Refresh DB'.")

st.divider()

st.markdown("""
### How to use this Dashboard
1. **Executive Overview**: High-level KPIs (Timeliness, Compliance, Safety Rates).
2. **Medication Safety**: Deep dive into ADRs, errors, and high-risk meds.
3. **Compliance**: Audit views and data quality reports.
""")
