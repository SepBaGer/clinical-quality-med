import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.sqlite_io import run_query

st.set_page_config(page_title="Executive Overview", layout="wide")

st.title("📊 Executive Overview")
st.markdown("High-level operational KPIs tracking timeliness, compliance, and safety outcomes.")

# Check for data
try:
    df_service = run_query("SELECT * FROM kpi_monthly_service")
    df_overall = run_query("SELECT * FROM kpi_monthly_overall")
    df_latest = run_query("SELECT MAX(month) as last_month FROM kpi_monthly_overall")
    last_month = df_latest['last_month'].iloc[0]
except:
    st.error("Database not ready or empty. Go to Home and click 'Build/Refresh DB'.")
    st.stop()

# --- Filters ---
with st.sidebar:
    st.header("Filters")
    month_list = sorted(df_service['month'].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", month_list, index=0)
    
    services = sorted(df_service['service_line'].unique())
    selected_services = st.multiselect("Service Lines", services, default=services)

# --- Filter Data ---
# For tiles: specific month
df_month_filtered = df_service[
    (df_service['month'] == selected_month) & 
    (df_service['service_line'].isin(selected_services))
]

# For trends: all months, filtered services
df_trend_filtered = df_service[df_service['service_line'].isin(selected_services)]

# Aggregations for Tiles (Weighted Averages based on totals)
total_enc = df_month_filtered['total_encounters'].sum()

def safe_rate(num, den):
    return (num / den) if den > 0 else 0

# Calc aggregate metrics for the selection
# We need to re-sum counts because rates aren't additive
enc_with_event = df_month_filtered['encounters_with_event'].sum()
enc_reported = df_month_filtered['encounters_reported'].sum()
enc_ontime = df_month_filtered['on_time_encounters'].sum()

compliance_rate = safe_rate(enc_reported, enc_with_event)
timeliness_rate = safe_rate(enc_ontime, enc_reported)

adr_count = df_month_filtered['adr_count'].sum()
severe_count = df_month_filtered['severe_count'].sum()
high_risk_count = df_month_filtered['high_risk_exposure_count'].sum()

adr_rate_1000 = safe_rate(adr_count, total_enc) * 1000
severe_rate_1000 = safe_rate(severe_count, total_enc) * 1000
high_risk_rate = safe_rate(high_risk_count, total_enc)

# --- GUI Layout ---

# Row 1: Tiles
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Encounters", f"{int(total_enc):,}", help="Total discharges/visits in period")
c2.metric("Compliance Rate", f"{compliance_rate:.1%}", help="Events Reported / Total Events Detected")
c3.metric("Timeliness Rate", f"{timeliness_rate:.1%}", help="Reported within 7 days")
c4.metric("High Risk Exposure", f"{high_risk_rate:.1%}", help="% Encounters with High Risk Meds")

c5, c6, c7, c8 = st.columns(4)
c5.metric("ADR Rate / 1k", f"{adr_rate_1000:.1f}")
c6.metric("Severe Events / 1k", f"{severe_rate_1000:.1f}")
c7.metric("ADR Raw Count", int(adr_count))
c8.metric("Severe Raw Count", int(severe_count))

st.divider()

# Row 2: Trends
col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    st.subheader("Severe Events per 1000 (Trend)")
    # Agg by month for trend line
    trend_agg = df_trend_filtered.groupby('month').agg({
        'severe_count': 'sum',
        'total_encounters': 'sum'
    }).reset_index()
    trend_agg['rate'] = (trend_agg['severe_count'] / trend_agg['total_encounters']) * 1000
    
    fig_sev = px.line(trend_agg, x='month', y='rate', markers=True, title="Severe Rate Trend")
    st.plotly_chart(fig_sev, use_container_width=True)

with col_trend2:
    st.subheader("Compliance & Timeliness Trend")
    trend_comp = df_trend_filtered.groupby('month').agg({
        'encounters_with_event': 'sum',
        'encounters_reported': 'sum',
        'on_time_encounters': 'sum'
    }).reset_index()
    trend_comp['Compliance'] = trend_comp['encounters_reported'] / trend_comp['encounters_with_event']
    trend_comp['Timeliness'] = trend_comp['on_time_encounters'] / trend_comp['encounters_reported']
    
    fig_comp = px.line(trend_comp, x='month', y=['Compliance', 'Timeliness'], markers=True, 
                       color_discrete_map={'Compliance': 'blue', 'Timeliness': 'green'})
    fig_comp.update_yaxes(range=[0, 1.1])
    st.plotly_chart(fig_comp, use_container_width=True)

# Row 3: Snapshot Table
st.subheader(f"Service Line Snapshot ({selected_month})")
st.dataframe(
    df_month_filtered.set_index('service_line')[
        ['total_encounters', 'compliance_rate', 'timeliness_rate', 'adr_per_1000', 'severe_per_1000']
    ].style.format({
        'compliance_rate': '{:.1%}',
        'timeliness_rate': '{:.1%}',
        'adr_per_1000': '{:.2f}',
        'severe_per_1000': '{:.2f}'
    }),
    use_container_width=True
)

# Export
csv_data = df_month_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Download Monthly Data (CSV)",
    csv_data,
    f"kpi_service_{selected_month}.csv",
    "text/csv"
)
