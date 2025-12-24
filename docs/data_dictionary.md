# Data Dictionary

## Core Tables

### `patients`

- **patient_id** (TEXT, PK): Unique identifier (e.g., `P-XXXXXX`).
- **age_band** (TEXT): Age group (`18-39`, `40-64`, `65+`).
- **sex** (TEXT): Biological sex (`F`, `M`, `Unknown`).

### `encounters`

- **encounter_id** (TEXT, PK): Unique identifier (e.g., `E-XXXXXX`).
- **patient_id** (TEXT, FK): Link to `patients`.
- **service_line** (TEXT): Clinical service (e.g., `Medicine`, `Surgery`, `ED`).
- **admission_type** (TEXT): Class of admission (`ED`, `Inpatient`, `Outpatient`).
- **admit_date** (DATE): Date of admission.
- **discharge_date** (DATE): Date of discharge.

### `med_orders`

- **med_order_id** (TEXT, PK): Unique identifier.
- **encounter_id** (TEXT, FK): Link to `encounters`.
- **med_class** (TEXT): Class of medication (e.g., `Opioid`).
- **high_risk_flag** (INT): `1` if the medication is considered high-risk (Opioid, Anticoagulant, Insulin, Sedative), else `0`.
- **order_date** (DATE): Date order was placed.

### `safety_events`

- **event_id** (TEXT, PK): Unique identifier.
- **encounter_id** (TEXT, FK): Link to `encounters`.
- **event_type** (TEXT): Classification (e.g., `ADR`, `Med_Error`).
- **severity** (TEXT): Clinical impact (`Mild`, `Moderate`, `Severe`).
- **report_delay_days** (INT): Days between event detection and reporting.
- **reported_flag** (INT): `1` if formally reported in the safety system.
- **event_date** (DATE): Date of the event occurrence.

## Derived Tables

### `encounter_facts` (Gold Table)

One row per encounter with pre-calculated flags.

- **length_of_stay_days**: `discharge_date - admit_date`.
- **med_orders_count**: Total meds ordered.
- **high_risk_exposure_flag**: `1` if any high-risk med was ordered.
- **adr_flag**: `1` if associated with an Adverse Drug Reaction (ADR).
- **med_error_flag**: `1` if associated with a Medication Error.
- **severe_event_flag**: `1` if associated with a `Severe` event.
- **reported_flag_any**: `1` if any event linked was reported.
- **on_time_flag_any**: `1` if any event was reported with `delay <= 7`.
- **readmission_30d_flag**: `1` if patient returned (any service) within 30 days of discharge.
- **ed_revisit_7d_flag**: `1` if patient returned to ED within 7 days of discharge.
