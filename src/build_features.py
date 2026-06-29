# src/build_features.py
import os
import sqlite3

DB_PATH = os.path.join("data", "sepsis_hospital.db")
SQL_SCRIPT_PATH = os.path.join("sql", "engineer_features.sql")

def compile_analytical_view():
    print("Connecting to relational clinical data warehouse...")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}. Please run seed_db.py first.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Reading temporal feature logic from {SQL_SCRIPT_PATH}...")
    with open(SQL_SCRIPT_PATH, "r") as f:
        sql_script = f.read()
        
    try:
        # Execute the multi-statement script to compile our database view
        print("Compiling SQL Analytic Window View (v_engineered_icu_vitals)...")
        cursor.executescript(sql_script)
        conn.commit()
        print("Success! SQL analytical feature layer compiled smoothly.")
        
        # Quick validation check: verify the view returns rows
        cursor.execute("SELECT COUNT(*) FROM v_engineered_icu_vitals LIMIT 1;")
        total_rows = cursor.fetchone()[0]
        print(f"Validation Pass: View is active with {total_rows:,} processed clinical rows.")
        
    except sqlite3.Error as e:
        print(f"SQL Execution Error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    compile_analytical_view()