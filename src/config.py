import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_NAME = "clinical_ops.db"
DB_PATH = DB_DIR / DB_NAME
SCHEMA_PATH = DB_DIR / "schema.sql"

# Parameters
RANDOM_SEED = 42
TARGET_N_PATIENTS = 500  # Small enough for rapid dev, large enough for charts
TARGET_N_ENCOUNTERS = 1200
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

# Business Rules / Lists
SERVICE_LINES = ["Medicine", "Surgery", "ED", "ICU", "OB", "Pediatrics", "Oncology"]
ADMISSION_TYPES = ["ED", "Inpatient", "Outpatient"]
MED_CLASSES = ["Opioid", "Antibiotic", "Anticoagulant", "Insulin", "Sedative", "Statin", "Bronchodilator"]
EVENT_TYPES = ["ADR", "Med_Error", "Near_Miss", "Allergy", "Interaction", "Omission"]
SEVERITIES = ["Mild", "Moderate", "Severe"]
