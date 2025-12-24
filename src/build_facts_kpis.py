import pandas as pd
import numpy as np
from src.sqlite_io import run_query, DB_PATH
import sqlite3

def build_encounter_facts():
    print("Building encounter_facts...")
    conn = sqlite3.connect(DB_PATH)
    
    # Load raw tables
    encounters = pd.read_sql("SELECT * FROM encounters", conn)
    med_orders = pd.read_sql("SELECT * FROM med_orders", conn)
    safety_events = pd.read_sql("SELECT * FROM safety_events", conn)
    
    # Pre-process Dates
    encounters['admit_date'] = pd.to_datetime(encounters['admit_date'])
    encounters['discharge_date'] = pd.to_datetime(encounters['discharge_date'])
    
    # 1. Med Orders Aggs
    # Count meds per encounter
    med_counts = med_orders.groupby('encounter_id').size().reset_index(name='med_orders_count')
    
    # High Risk Flag: if any med is high risk
    high_risk = med_orders.groupby('encounter_id')['high_risk_flag'].max().reset_index(name='high_risk_exposure_flag')
    
    # 2. Safety Events Aggs
    # We need to know if any event linked to encounter has certain properties
    if not safety_events.empty:
        # ADR
        adr_ids = safety_events[safety_events['event_type'] == 'ADR']['encounter_id'].unique()
        # Med Error
        med_error_ids = safety_events[safety_events['event_type'] == 'Med_Error']['encounter_id'].unique()
        # Severe
        severe_ids = safety_events[safety_events['severity'] == 'Severe']['encounter_id'].unique()
        # Reported
        reported_ids = safety_events[safety_events['reported_flag'] == 1]['encounter_id'].unique()
        # On Time (reported_flag=1 AND delay <= 7)
        on_time_ids = safety_events[
            (safety_events['reported_flag'] == 1) & 
            (safety_events['report_delay_days'] <= 7)
        ]['encounter_id'].unique()
        # Late (reported_flag=1 AND delay > 7)
        late_ids = safety_events[
            (safety_events['reported_flag'] == 1) & 
            (safety_events['report_delay_days'] > 7)
        ]['encounter_id'].unique()
    else:
        adr_ids, med_error_ids, severe_ids, reported_ids, on_time_ids, late_ids = [], [], [], [], [], []

    # Merge into encounters
    df = encounters.copy()
    
    # Merge Meds
    df = df.merge(med_counts, on='encounter_id', how='left').fillna({'med_orders_count': 0})
    df = df.merge(high_risk, on='encounter_id', how='left').fillna({'high_risk_exposure_flag': 0})
    
    # Flags from Events
    df['adr_flag'] = df['encounter_id'].isin(adr_ids).astype(int)
    df['med_error_flag'] = df['encounter_id'].isin(med_error_ids).astype(int)
    df['severe_event_flag'] = df['encounter_id'].isin(severe_ids).astype(int)
    df['reported_flag_any'] = df['encounter_id'].isin(reported_ids).astype(int)
    df['on_time_flag_any'] = df['encounter_id'].isin(on_time_ids).astype(int)
    df['late_reporting_flag_any'] = df['encounter_id'].isin(late_ids).astype(int)
    
    # Length of stay
    df['length_of_stay_days'] = (df['discharge_date'] - df['admit_date']).dt.days
    
    # 3. Readmissions & ED Revisit (Window Functions)
    df.sort_values(by=['patient_id', 'admit_date'], inplace=True)
    
    # Next admission
    df['next_admit_date'] = df.groupby('patient_id')['admit_date'].shift(-1)
    df['next_admission_type'] = df.groupby('patient_id')['admission_type'].shift(-1)
    
    # Days to next admit from discharge
    # If next_admit exists, calc delta
    df['days_to_next'] = (df['next_admit_date'] - df['discharge_date']).dt.days
    
    # Logic: Readmission <= 30 days
    df['readmission_30d_flag'] = ((df['days_to_next'] <= 30) & (df['days_to_next'] >= 0)).astype(int)
    
    # Logic: ED Revisit <= 7 days AND next is ED
    df['ed_revisit_7d_flag'] = (
        (df['days_to_next'] <= 7) & 
        (df['days_to_next'] >= 0) & 
        (df['next_admission_type'] == 'ED')
    ).astype(int)
    
    # Clean up temp cols
    df.drop(columns=['next_admit_date', 'next_admission_type', 'days_to_next'], inplace=True)
    
    # Convert dates back to string for SQLite or keep as is (pandas writes timestamp, read back as str usually)
    # Ensuring standard basic types
    df['admit_date'] = df['admit_date'].dt.date
    df['discharge_date'] = df['discharge_date'].dt.date
    
    # Write to DB
    df.to_sql("encounter_facts", conn, if_exists="replace", index=False)
    print(f"encounter_facts built: {len(df)} rows.")
    conn.close()

def build_kpis():
    print("Building KPI tables...")
    conn = sqlite3.connect(DB_PATH)
    facts = pd.read_sql("SELECT * FROM encounter_facts", conn)
    med_orders = pd.read_sql("SELECT * FROM med_orders", conn) # for denom
    safety_events = pd.read_sql("SELECT * FROM safety_events", conn)
    
    # Ensure Month column
    facts['month'] = pd.to_datetime(facts['admit_date']).dt.strftime('%Y-%m')
    
    # --- 6. KPI Monthly Service ---
    # Aggregations
    # Timeliness Rate = sum(on_time_flag_any) / sum(reported_flag_any)
    # Compliance Rate = sum(reported_flag_any) / count(where linked to event) -> Wait.
    # Definition in PROMPT:
    # Compliance rate = encounters_with_reported_event / encounters_with_any_event
    # We need a flag "any_event_linked". 
    # Let's add it via logic: if adr_flag or med_error_flag or severe_flag or ... wait.
    # Best way: check if encounter_id is in safety_events table.
    # In encounter_facts, we don't strictly have "has_event", but we can infer if any flag is set? 
    # No, event might be Type="Other" and Severity="Mild" and Not Reported -> flags might be 0.
    # Let's fix encounter_facts to include 'has_any_event' later? Or just join safely.
    # BETTER: Aggregation from facts is easier. Let's assume 'reported_flag_any' implies event.
    # But for denominator of compliance, we need all events.
    
    # Recover 'has_event' from join with safety_events distinct IDs
    event_enc_ids = pd.read_sql("SELECT DISTINCT encounter_id FROM safety_events", conn)['encounter_id']
    facts['has_any_event'] = facts['encounter_id'].isin(event_enc_ids).astype(int)
    
    grp = facts.groupby(['month', 'service_line'])
    
    kpi_service = pd.DataFrame()
    kpi_service['total_encounters'] = grp.size()
    kpi_service['encounters_with_event'] = grp['has_any_event'].sum()
    kpi_service['encounters_reported'] = grp['reported_flag_any'].sum()
    kpi_service['on_time_encounters'] = grp['on_time_flag_any'].sum()
    
    kpi_service['compliance_rate'] = kpi_service['encounters_reported'] / kpi_service['encounters_with_event'].replace(0, np.nan)
    kpi_service['timeliness_rate'] = kpi_service['on_time_encounters'] / kpi_service['encounters_reported'].replace(0, np.nan)
    
    # Safety Rates (per 1000 encounters)
    kpi_service['adr_count'] = grp['adr_flag'].sum()
    kpi_service['severe_count'] = grp['severe_event_flag'].sum()
    kpi_service['high_risk_exposure_count'] = grp['high_risk_exposure_flag'].sum()
    
    kpi_service['adr_per_1000'] = (kpi_service['adr_count'] / kpi_service['total_encounters']) * 1000
    kpi_service['severe_per_1000'] = (kpi_service['severe_count'] / kpi_service['total_encounters']) * 1000
    kpi_service['high_risk_exposure_rate'] = kpi_service['high_risk_exposure_count'] / kpi_service['total_encounters']
    
    kpi_service.reset_index(inplace=True)
    kpi_service.fillna(0, inplace=True)
    kpi_service.to_sql("kpi_monthly_service", conn, if_exists="replace", index=False)

    # --- 7. KPI Monthly Overall ---
    # Similar but without service_line
    grp_all = facts.groupby(['month'])
    kpi_overall = pd.DataFrame()
    kpi_overall['total_encounters'] = grp_all.size()
    # reuse basic logic...
    kpi_overall['adr_per_1000'] = (grp_all['adr_flag'].sum() / kpi_overall['total_encounters']) * 1000
    kpi_overall.reset_index(inplace=True)
    kpi_overall.to_sql("kpi_monthly_overall", conn, if_exists="replace", index=False)

    # --- 8. Event Metrics Monthly ---
    # Need granular view: Month, Service, MedClass (from orders? No, from Facts + Event link?)
    # The prompt asks for "event_metrics_monthly"
    # Let's join Events -> Encounters to get Service/Month, and join MedOrders?
    # Events have med_class? No. MedOrders have med_class.
    # Relation: MedOrder -> Encounter -> Event. 
    # Usually we don't know WHICH med caused the event in this schema unless we link them. 
    # For synthetic demo, let's just aggregate by Service/Month/EventType.
    
    files_df = safety_events.merge(facts[['encounter_id', 'service_line', 'month']], on='encounter_id', how='left')
    metrics = files_df.groupby(['month', 'service_line', 'event_type']).size().reset_index(name='event_count')
    metrics.to_sql("event_metrics_monthly", conn, if_exists="replace", index=False)
    
    # --- 9. Reporting Delay Bins ---
    # Bins: 0-1, 2-3, 4-7, 8-14, 15-30, 31+
    # On safety_events
    bins = [-1, 1, 3, 7, 14, 30, 999]
    labels = ["0-1", "2-3", "4-7", "8-14", "15-30", "31+"]
    safety_events['delay_bin'] = pd.cut(safety_events['report_delay_days'], bins=bins, labels=labels)
    # Join for service line
    se_enriched = safety_events.merge(facts[['encounter_id', 'service_line', 'month']], on='encounter_id', how='left')
    
    delay_bins = se_enriched.groupby(['month', 'service_line', 'delay_bin']).size().reset_index(name='count')
    delay_bins.to_sql("reporting_delay_bins", conn, if_exists="replace", index=False)
    
    # --- 10. Audit View ---
    # Criteria: High Risk = 1 AND (ADR or MedError or Severe) AND Late Reporting = 1
    # We can filter encounter_facts directly?
    # encounter_facts has: high_risk_exposure_flag, adr_flag, med_error_flag, severe_event_flag, late_reporting_flag_any
    audit_mask = (
        (facts['high_risk_exposure_flag'] == 1) &
        ((facts['adr_flag'] == 1) | (facts['med_error_flag'] == 1) | (facts['severe_event_flag'] == 1)) &
        (facts['late_reporting_flag_any'] == 1)
    )
    audit_view = facts[audit_mask].copy()
    audit_view.to_sql("audit_view", conn, if_exists="replace", index=False)
    
    # --- 11. Data Quality Report ---
    # Simple checks
    dq_data = []
    # Check 1: Orphans (Safety events without encounter)
    orphans = safety_events[~safety_events['encounter_id'].isin(facts['encounter_id'])]
    dq_data.append({"check": "Safety Events Orphans", "status": "PASS" if orphans.empty else "FAIL", "count": len(orphans)})
    
    # Check 2: Negative LOS
    neg_los = facts[facts['length_of_stay_days'] < 0]
    dq_data.append({"check": "Negative LOS", "status": "PASS" if neg_los.empty else "FAIL", "count": len(neg_los)})
    
    dq_df = pd.DataFrame(dq_data)
    dq_df.to_sql("data_quality_report", conn, if_exists="replace", index=False)
    
    conn.close()
    print("KPIs built successfully.")

def run_pipeline():
    build_encounter_facts()
    build_kpis()

if __name__ == "__main__":
    run_pipeline()
