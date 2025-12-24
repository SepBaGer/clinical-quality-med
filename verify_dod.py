import sqlite3
import os

DB_PATH = "db/clinical_ops.db"

print("=== DoD VERIFICATION REPORT ===\n")

# 1. Check DB exists
print(f"[1] DB Exists: {os.path.exists(DB_PATH)}")

# 2. Check all required tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print(f"[2] Tables Found: {tables}")

required = ["patients", "encounters", "med_orders", "safety_events", 
            "encounter_facts", "kpi_monthly_service", "kpi_monthly_overall",
            "event_metrics_monthly", "reporting_delay_bins", "audit_view", "data_quality_report"]

missing = [t for t in required if t not in tables]
print(f"    Missing Tables: {missing if missing else 'NONE (All Present)'}")

# 3. Row counts
for t in required:
    if t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"    {t}: {count} rows")

# 4. encounter_facts uniqueness
cursor.execute("SELECT COUNT(*) FROM encounter_facts")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(DISTINCT encounter_id) FROM encounter_facts")
unique = cursor.fetchone()[0]
print(f"\n[3] encounter_facts Integrity: {total} total, {unique} unique -> {'PASS' if total == unique else 'FAIL'}")

# 5. Data Quality Report
cursor.execute("SELECT * FROM data_quality_report")
dq = cursor.fetchall()
print(f"\n[4] Data Quality Checks:")
for row in dq:
    print(f"    {row}")

conn.close()
print("\n=== END REPORT ===")
