# src/seed_db.py
import os
import glob
import pandas as pd
import sqlite3

# Define relative paths matching our folder layout
RAW_DATA_DIR = os.path.join("data", "raw")
DB_PATH = os.path.join("data", "sepsis_hospital.db")

def create_database():
    print("Initializing local database setup...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Complete, production-grade schema layout matching all 40+ raw clinical columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS icu_vitals (
        patient_id TEXT,
        hour_idx INT,
        HR REAL,
        O2Sat REAL,
        Temp REAL,
        SBP REAL,
        MAP REAL,
        DBP REAL,
        Resp REAL,
        EtCO2 REAL,
        BaseExcess REAL,
        HCO3 REAL,
        FiO2 REAL,
        pH REAL,
        PaCO2 REAL,
        SaO2 REAL,
        AST REAL,
        BUN REAL,
        Alkalinephos REAL,
        Calcium REAL,
        Chloride REAL,
        Creatinine REAL,
        Bilirubin_direct REAL,
        Glucose REAL,
        Lactate REAL,
        Magnesium REAL,
        Phosphate REAL,
        Potassium REAL,
        Bilirubin_total REAL,
        Hct REAL,
        Hgb REAL,
        PTT REAL,
        WBC REAL,
        Fibrinogen REAL,
        Platelets REAL,
        Age REAL,
        Gender INT,
        Unit1 REAL,
        Unit2 REAL,
        HospAdmTime REAL,
        ICULOS INT,
        SepsisLabel INT,
        TroponinI REAL,  
        PaO2 REAL        
    );
    """)
    conn.commit()
    return conn

def seed_data(conn):
    # Match any .psv file inside data/raw/
    psv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.psv"))
    total_files = len(psv_files)
    
    if total_files == 0:
        print(f"Error: No .psv files found in '{RAW_DATA_DIR}'.")
        print("Ensure your downloaded training files are unzipped inside 'data/raw/'.")
        return
        
    print(f"Found {total_files} patient files. Commencing relational ingestion...")
    
    chunk_size = 500
    records_buffer = []
    
    for idx, file_path in enumerate(psv_files):
        # Isolate file names to create clean string tracking indices
        patient_id = os.path.basename(file_path).replace(".psv", "")
        
        # Read the individual pipe-separated patient file
        df_patient = pd.read_csv(file_path, sep="|")
        
        # Track the time series index cleanly
        df_patient.insert(0, 'patient_id', patient_id)
        df_patient.insert(1, 'hour_idx', range(len(df_patient)))
        
        records_buffer.append(df_patient)
        
        # Flush the accumulated rows into the DB to keep memory footprints low
        if (idx + 1) % chunk_size == 0 or (idx + 1) == total_files:
            combined_df = pd.concat(records_buffer, ignore_index=True)
            combined_df.to_sql("icu_vitals", conn, if_exists="append", index=False)
            records_buffer = []
            print(f" Processed tracking: {idx + 1}/{total_files} patient files securely migrated.")

    print("Database completely seeded and optimized!")

if __name__ == "__main__":
    # Make sure old broken database is dropped before starting
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed old database to clear structural schema mismatch.")
        except Exception as e:
            print(f"Could not delete database automatically: {e}. Please manually clear it.")
            
    connection = create_database()
    seed_data(connection)
    connection.close()