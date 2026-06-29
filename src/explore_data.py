# src/explore_data.py
import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join("data", "sepsis_hospital.db")

def run_sql_eda():
    print("Connecting to relational clinical warehouse for baseline EDA...")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}. Run seed_db.py first.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    
    print("\nQuestion 1: What is the baseline incidence rate of sepsis in our ICU population?")

    q1_query = """
    SELECT 
        SepsisLabel, 
        COUNT(DISTINCT patient_id) AS total_patients,
        ROUND(COUNT(DISTINCT patient_id) * 100.0 / (SELECT COUNT(DISTINCT patient_id) FROM icu_vitals), 2) AS population_percentage
    FROM icu_vitals
    GROUP BY SepsisLabel;
    """
    df_q1 = pd.read_sql_query(q1_query, conn)
    print(df_q1.to_string(index=False))
    
    print("\nQuestion 2: What is the average respiratory rate (and other baseline vitals) for patients split by outcome?")

    q2_query = """
    SELECT 
        SepsisLabel, 
        ROUND(AVG(Resp), 2) AS avg_resp_rate,
        ROUND(AVG(HR), 2) AS avg_heart_rate,
        ROUND(AVG(Temp), 2) AS avg_core_temp
    FROM icu_vitals
    GROUP BY SepsisLabel;
    """
    df_q2 = pd.read_sql_query(q2_query, conn)
    print(df_q2.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    run_sql_eda()