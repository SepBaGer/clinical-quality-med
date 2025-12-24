-- Core Tables
DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    age_band TEXT,
    sex TEXT
);

DROP TABLE IF EXISTS encounters;
CREATE TABLE encounters (
    encounter_id TEXT PRIMARY KEY,
    patient_id TEXT,
    service_line TEXT,
    admission_type TEXT,
    admit_date DATE,
    discharge_date DATE,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
);

DROP TABLE IF EXISTS med_orders;
CREATE TABLE med_orders (
    med_order_id TEXT PRIMARY KEY,
    encounter_id TEXT,
    med_class TEXT,
    high_risk_flag INTEGER,
    order_date DATE,
    FOREIGN KEY(encounter_id) REFERENCES encounters(encounter_id)
);

DROP TABLE IF EXISTS safety_events;
CREATE TABLE safety_events (
    event_id TEXT PRIMARY KEY,
    encounter_id TEXT,
    event_type TEXT,
    severity TEXT,
    report_delay_days INTEGER,
    reported_flag INTEGER,
    event_date DATE,
    FOREIGN KEY(encounter_id) REFERENCES encounters(encounter_id)
);

-- Derived Tables (Schema Definitions for Consistency)
DROP TABLE IF EXISTS encounter_facts;
CREATE TABLE encounter_facts (
    encounter_id TEXT PRIMARY KEY,
    patient_id TEXT,
    service_line TEXT,
    admission_type TEXT,
    admit_date DATE,
    discharge_date DATE,
    length_of_stay_days INTEGER,
    med_orders_count INTEGER,
    high_risk_exposure_flag INTEGER,
    adr_flag INTEGER,
    med_error_flag INTEGER,
    severe_event_flag INTEGER,
    reported_flag_any INTEGER,
    on_time_flag_any INTEGER,
    late_reporting_flag_any INTEGER,
    readmission_30d_flag INTEGER,
    ed_revisit_7d_flag INTEGER
);

-- KPI Tables will be created dynamically via pandas to_sql to allow for flexible metrics aggregation,
-- but we ensure the core analytic table (encounter_facts) is strictly defined.
