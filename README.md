# Clinical Quality & Medication Safety Operations Dashboard (Synthetic Model)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive analytics portfolio project demonstrating **operational orchestration** in a clinical context. This repository contains an end-to-end pipeline: from synthetic data generation (SQLite) to an audit-ready interactive dashboard.

> **⚠️ DISCLAIMER**: All data is **100% SYNTHETIC**, generated via Python scripts. It does not contain Protected Health Information (PHI) and should not be used for actual clinical decision-making.

## 🎯 Mission

To demonstrate the role of a **Clinical Quality Ops Orchestrator** by building a tool that tracks:

- **Timeliness & Compliance**: Operational efficiency in safety reporting.
- **Clinical Outcomes**: ADR rates, readmissions, and severe events.
- **Audit Readiness**: Transparent logic and row-level traceability.

## 🚀 Features

- **Reproducible Pipeline**: One-click "Build/Refresh DB" button rebuilds the SQLite database from scratch.
- **Gold Table Architecture**: Centralized `encounter_facts` table for consistent KPI definitions.
- **Audit Worklist**: Auto-flagging of high-risk, late-reported safety events.
- **Quality Gates**: Automated checks for data integrity (e.g., negative LOS, orphans).

## 🛠️ Tech Stack

- **Python**: Data generation and processing (`pandas`, `numpy`).
- **SQLite**: Local relational database.
- **Streamlit**: Interactive web dashboard.
- **Plotly**: Data visualization.
- **GitHub**: Version control and CI/CD readiness.

## 📂 Structure

```
├── app/
│   ├── app.py                 # Home & Orchestrator
│   └── pages/                 # Deep-dive dashboards
│       ├── 1_Executive_Overview.py
│       ├── 2_Medication_Safety.py
│       └── 3_Compliance_Data_Quality.py
├── db/                        # SQLite Database & Schema
├── docs/                      # Business Logic & KPIs
├── src/                       # ETL & Data Logic
└── requirements.txt
```

## ⚡ Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/Start-Here-DELL/clinical-quality-med-safety-dashboard.git
   cd clinical-quality-med-safety-dashboard
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard**

   ```bash
   streamlit run app/app.py
   ```

4. **Initialize Data**
   - Open the app in your browser.
   - Click the **"🏗️ Build / Refresh DB"** button to generate synthetic data and calculate KPIs.

## 📊 Key Metrics (See `docs/kpi_definitions.md`)

- **Timeliness**: % of events reported within 7 days.
- **Readmission**: % of patients returning within 30 days.
- **High Risk Exposure**: Encounters with Opioids, Insulin, or Anticoagulants.

## 📄 License

MIT.
