import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.sqlite_io import run_query

st.set_page_config(page_title="Compliance & Data Quality", layout="wide")
st.title("🛡️ Compliance & Data Quality")

# Load Data
try:
    df_bins = run_query("SELECT * FROM reporting_delay_bins")
    df_audit = run_query("SELECT * FROM audit_view")
    df_dq = run_query("SELECT * FROM data_quality_report")
except:
    st.error("Build DB first.")
    st.stop()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Reporting Timeliness", "Audit Worklist", "Data Quality"])

with tab1:
    st.subheader("Reporting Delay Distribution")
    # Filter by service?
    services = st.multiselect("Filter Service Line", sorted(df_bins['service_line'].unique()), default=sorted(df_bins['service_line'].unique()))
    
    df_bins_filt = df_bins[df_bins['service_line'].isin(services)]
    
    # Agg
    bin_agg = df_bins_filt.groupby('delay_bin')['count'].sum().reset_index()
    # Ensure order
    order_map = {"0-1":1, "2-3":2, "4-7":3, "8-14":4, "15-30":5, "31+":6}
    bin_agg['order'] = bin_agg['delay_bin'].map(order_map)
    bin_agg.sort_values('order', inplace=True)
    
    fig = px.bar(bin_agg, x='delay_bin', y='count', title="Events by Reporting Delay (Days)", text_auto=True)
    fig.add_vrect(x0=-0.5, x1=2.5, annotation_text="On Time (<=7)", annotation_position="top left", fillcolor="green", opacity=0.1, line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("⚠️ Audit Worklist: High Risk + Adverse Event + Late Reporting")
    st.markdown("Encounters requiring immediate operational review.")
    
    if not df_audit.empty:
        st.dataframe(
            df_audit[['encounter_id', 'service_line', 'admit_date', 'med_orders_count', 'length_of_stay_days']],
            use_container_width=True
        )
        csv_audit = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button("Download Audit List (CSV)", csv_audit, "audit_worklist.csv", "text/csv")
    else:
        st.success("No encounters match the critical audit criteria! (Clean dashboard)")

with tab3:
    st.subheader("Pipeline Health & Logic Checks")
    
    for _, row in df_dq.iterrows():
        status_color = "green" if row['status'] == 'PASS' else "red"
        st.markdown(f"**{row['check']}**: :{status_color}[{row['status']}] (Count: {row['count']})")
    
    st.info("System timestamp: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
