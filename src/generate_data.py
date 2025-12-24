import pandas as pd
import numpy as np
import uuid
import random
from src.config import (
    SERVICE_LINES, ADMISSION_TYPES, MED_CLASSES, EVENT_TYPES, SEVERITIES,
    TARGET_N_PATIENTS, TARGET_N_ENCOUNTERS, START_DATE, END_DATE, RANDOM_SEED, DB_PATH
)
from src.sqlite_io import init_db
import sqlite3

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

import pandas as pd
import numpy as np
import uuid
import random
from src.config import (
    SERVICE_LINES, ADMISSION_TYPES, MED_CLASSES, EVENT_TYPES, SEVERITIES,
    TARGET_N_PATIENTS, TARGET_N_ENCOUNTERS, START_DATE, END_DATE, RANDOM_SEED, DB_PATH
)
from src.sqlite_io import init_db
import sqlite3

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

def generate_patients(n=TARGET_N_PATIENTS):
    data = []
    for _ in range(n):
        pid = f"P-{str(uuid.uuid4())[:8]}"
        age = np.random.choice(["18-39", "40-64", "65+"], p=[0.3, 0.4, 0.3])
        sex = np.random.choice(["F", "M", "Unknown"], p=[0.5, 0.45, 0.05])
        data.append((pid, age, sex))
    return pd.DataFrame(data, columns=["patient_id", "age_band", "sex"])

def generate_encounters(patients_df, n=TARGET_N_ENCOUNTERS):
    data = []
    patient_ids = patients_df["patient_id"].values
    dates = pd.date_range(START_DATE, END_DATE).to_series()
    
    for _ in range(n):
        eid = f"E-{str(uuid.uuid4())[:8]}"
        pid = np.random.choice(patient_ids)
        svc = np.random.choice(SERVICE_LINES)
        adm_type = np.random.choice(ADMISSION_TYPES, p=[0.4, 0.4, 0.2])
        
        admit = dates.sample(1).iloc[0]
        los = int(np.random.gamma(shape=2, scale=3)) + 1 
        discharge = admit + pd.Timedelta(days=los)
        
        data.append((eid, pid, svc, adm_type, admit.date(), discharge.date()))
        
    return pd.DataFrame(data, columns=["encounter_id", "patient_id", "service_line", "admission_type", "admit_date", "discharge_date"])

def generate_med_orders(encounters_df):
    data = []
    # High risk classes
    high_risk_classes = ["Opioid", "Anticoagulant", "Insulin", "Sedative"]
    
    for _, row in encounters_df.iterrows():
        eid = row["encounter_id"]
        # Random number of meds per encounter (0 to 8)
        n_meds = np.random.randint(0, 9)
        
        for _ in range(n_meds):
            mid = f"M-{str(uuid.uuid4())[:8]}"
            mclass = np.random.choice(MED_CLASSES)
            
            # High risk logic: if class is in high_risk_classes, flag=1 logic with high prob, 
            # but to be simple we just define the flag by the class logic strictly or with noise.
            # Let's say: High Risk Class always = High Risk Flag for simplicity of metrics,
            # or maybe 90% chance. Let's make it deterministic for clarity.
            is_high_risk = 1 if mclass in high_risk_classes else 0
            
            # Order date between admit and discharge
            # approximate by admit date
            odate = row["admit_date"]
            
            data.append((mid, eid, mclass, is_high_risk, odate))
            
    return pd.DataFrame(data, columns=["med_order_id", "encounter_id", "med_class", "high_risk_flag", "order_date"])

def generate_safety_events(encounters_df, med_orders_df):
    data = []
    # Event rate: say 10% of encounters have an event
    n_encounters = len(encounters_df)
    n_events = int(n_encounters * 0.15) # 15% rate
    
    target_encounters = encounters_df.sample(n_events)
    
    for _, row in target_encounters.iterrows():
        ev_id = f"EV-{str(uuid.uuid4())[:8]}"
        eid = row["encounter_id"]
        
        ev_type = np.random.choice(EVENT_TYPES)
        
        # Severity distribution
        severity = np.random.choice(SEVERITIES, p=[0.6, 0.3, 0.1]) # 10% severe
        
        # Reporting Delay
        # 60% on time (<=7), 40% late (>7)
        if np.random.random() < 0.6:
            delay = np.random.randint(0, 8)
        else:
            delay = np.random.randint(8, 45)
            
        # Reported flag (Compliance)
        # 90% reported
        reported = 1 if np.random.random() < 0.9 else 0
        
        # Event date
        ev_date = row["discharge_date"] # Simplified: detected at discharge/post-discharge usually
        
        data.append((ev_id, eid, ev_type, severity, delay, reported, ev_date))
        
    return pd.DataFrame(data, columns=["event_id", "encounter_id", "event_type", "severity", "report_delay_days", "reported_flag", "event_date"])

def run_data_generation():
    print("Generating synthetic data...")
    patients_df = generate_patients()
    encounters_df = generate_encounters(patients_df)
    med_orders_df = generate_med_orders(encounters_df)
    safety_events_df = generate_safety_events(encounters_df, med_orders_df)
    
    print(f"Generated: {len(patients_df)} Patients, {len(encounters_df)} Encounters, {len(med_orders_df)} MedOrders, {len(safety_events_df)} Events.")
    
    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    # Use replace to ensure fresh data on rebuild
    patients_df.to_sql("patients", conn, if_exists="replace", index=False)
    encounters_df.to_sql("encounters", conn, if_exists="replace", index=False)
    med_orders_df.to_sql("med_orders", conn, if_exists="replace", index=False)
    safety_events_df.to_sql("safety_events", conn, if_exists="replace", index=False)
    conn.close()
    print("Data inserted into SQLite.")

if __name__ == "__main__":
    init_db()
    run_data_generation()

if __name__ == "__main__":
    init_db()
    run_data_generation()
