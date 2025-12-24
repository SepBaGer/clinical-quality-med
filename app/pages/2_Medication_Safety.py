import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.sqlite_io import run_query

st.set_page_config(page_title="Medication Safety", layout="wide")
st.title("💊 Medication Safety Deep Dive")

try:
    df_metrics = run_query("SELECT * FROM event_metrics_monthly")
    # We also need context for high risk exposure which is in kpi_service
    df_kpi = run_query("SELECT * FROM kpi_monthly_service")
except:
    st.error("Data missing. Build DB first.")
    st.stop()

# --- Filters ---
with st.sidebar:
    all_services = sorted(df_metrics['service_line'].unique())
    selected_service = st.multiselect("Service Line", all_services, default=all_services)
    
    all_types = sorted(df_metrics['event_type'].unique())
    selected_types = st.multiselect("Event Type", all_types, default=all_types)

# Filter
df_m_filt = df_metrics[
    (df_metrics['service_line'].isin(selected_service)) &
    (df_metrics['event_type'].isin(selected_types))
]

df_kpi_filt = df_kpi[df_kpi['service_line'].isin(selected_service)]

# Layout

col1, col2 = st.columns(2)

with col1:
    st.subheader("Event Count by Type (Aggregated)")
    group_type = df_m_filt.groupby('event_type')['event_count'].sum().reset_index()
    fig_bar = px.bar(group_type, x='event_type', y='event_count', color='event_type')
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("High Risk Exposure Rate Trend")
    # Trend over time (avg of selected services weighted? Or just boxplot? Let's do line chart by service)
    # kpi table has high_risk_exposure_rate
    fig_line = px.line(df_kpi_filt, x='month', y='high_risk_exposure_rate', color='service_line')
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

st.subheader("Event Heatmap (Month vs Service)")
# Aggregate counts
heatmap_data = df_m_filt.groupby(['month', 'service_line'])['event_count'].sum().reset_index()
fig_heat = px.density_heatmap(heatmap_data, x='month', y='service_line', z='event_count', color_continuous_scale="Reds")
st.plotly_chart(fig_heat, use_container_width=True)

with st.expander("Raw Metrics Data"):
    st.dataframe(df_m_filt)
    csv = df_m_filt.to_csv(index=False).encode('utf-8')
    st.download_button("Download Event Metrics", csv, "event_metrics.csv", "text/csv")
