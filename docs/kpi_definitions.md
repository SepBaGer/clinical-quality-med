# KPI Definitions

## Timeliness

**Metric**: Timeliness Rate

- **Numerator**: Encounters with at least one event reported "on time" (`report_delay_days <= 7`).
- **Denominator**: Encounters with at least one reported event.
- **Formula**: `sum(on_time_flag_any) / sum(reported_flag_any)`
- **Goal**: > 90%

## Compliance (Reporting)

**Metric**: Compliance Rate

- **Numerator**: Encounters with at least one *reported* safety event.
- **Denominator**: Encounters with *known* safety events (detected via triggers/audit).
- **Note**: In this synthetic dataset, we simulate "unreported" events to measure this gap.
- **Formula**: `encounters_reported / encounters_with_any_event`

## Safety Rates

**Metric**: ADR Rate per 1000

- **Formula**: `(Count of Encounters with ADR / Total Encounters) * 1000`

**Metric**: Severe Event Rate per 1000

- **Formula**: `(Count of Encounters with Severe Event / Total Encounters) * 1000`

## High Risk Exposure

**Metric**: High Risk Exposure Rate

- **Definition**: % of encounters where the patient received at least one high-risk medication (Opioid, Insulin, Anticoagulant, Sedative).
- **Formula**: `sum(high_risk_exposure_flag) / total_encounters`

## Readmission

**Metric**: 30-Day Readmission Rate

- **Definition**: Proportion of discharges followed by another admission for the same patient within 30 days.
- **Formula**: `sum(readmission_30d_flag) / total_discharges`
