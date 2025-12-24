import sqlite3
import pandas as pd
from src.config import DB_PATH, SCHEMA_PATH

def init_db():
    """Drops and recreates the tables using schema.sql."""
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True)
        
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        schema_script = f.read()
    conn.executescript(schema_script)
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def run_query(query, params=None):
    """Executes a read query and returns a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def execute_statement(statement, params=None):
    """Executes a write statement (INSERT, UPDATE, DELETE)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(statement, params)
        else:
            cursor.execute(statement)
        conn.commit()
    finally:
        conn.close()
