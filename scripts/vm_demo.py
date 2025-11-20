# vm_demo.py — Linear, step-by-step demo for self-managed MySQL on a VM
# Run this file top-to-bottom OR run it cell-by-cell in VS Code.
# Prereqs:
#   pip install sqlalchemy pymysql pandas python-dotenv
#
# Env vars (populate a local .env):
#   VM_DB_HOST, VM_DB_PORT, VM_DB_USER, VM_DB_PASS, VM_DB_NAME

import os
import time
import sys
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- 0) Load environment and Validate (FIXED FOR ROBUSTNESS) ---
# NOTE: The path is set to look for .env in the current directory for better portability.
# Ensure your .env file is in the same directory you run the script from!
load_dotenv(".env")

VM_DB_HOST = os.getenv("VM_DV_HOST", "35.184.55.201")
VM_DB_PORT = os.getenv("VM_DB_PORT", "3306")
VM_DB_USER = os.getenv("VM_DV_USER", "aaravdb")
VM_DB_PASS = os.getenv("VM_DB_PASS", "StonyBrook")
VM_DB_NAME = os.getenv("VM_DB_NAME", "class_db_aarav2003")

print("[ENV] VM_DB_HOST:", VM_DB_HOST)
print("[ENV] VM_DB_PORT:", VM_DB_PORT)
print("[ENV] VM_DB_USER:", VM_DB_USER)
print("[ENV] VM_DB_NAME:", VM_DB_NAME)

# CRITICAL CHECK: Exit if host is missing (prevents immediate crash if .env fails)
if not VM_DB_HOST or not VM_DB_USER or not VM_DB_PASS or not VM_DB_NAME:
    print("\n[ERROR] Missing one or more required environment variables (VM_DB_HOST, VM_DB_USER, VM_DB_PASS, VM_DB_NAME).")
    print("        Please check your .env file for correct casing and values.")
    sys.exit(1)


# --- 1) Connect to server (no DB) and ensure database exists ---
# Construct the server URL. Note: We do not include VM_DB_NAME here.
server_url = f"mysql+pymysql://{VM_DB_USER}:{VM_DB_PASS}@{VM_DB_HOST}:{VM_DB_PORT}/?ssl=false"

# Mask password in output for security
masked_url = server_url.replace(VM_DB_PASS, "*****") 

print("\n" + "="*50)
print(f"[STEP 1] Connecting to MySQL VM ({VM_DB_HOST}): {masked_url}")
t0 = time.time()

try:
    # Use pool_pre_ping for connection testing, removed redundant connect_args
    engine_server = create_engine(server_url, pool_pre_ping=True)
    
    with engine_server.connect() as conn:
        # Check if the connection works and create the database
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{VM_DB_NAME}`"))
        conn.commit()
    print(f"[OK] Ensured database `{VM_DB_NAME}` exists.")

except Exception as e:
    print("\n[CRITICAL ERROR] Failed to connect to VM MySQL Server in Step 1.")
    print("Please check the following:")
    print("1. Firewall: Is tcp:3306 open to your current public IP address?")
    print("2. VM Config: Is 'bind-address = 0.0.0.0' set in /etc/mysql/mysql.conf.d/mysqld.cnf?")
    print("3. Credentials: Are VM_DB_USER and VM_DB_PASS correct in .env?")
    print(f"Details: {e}")
    sys.exit(1)


# --- 2) Connect to the target database ---
# Construct the database URL, including the database name
db_url = f"mysql+pymysql://{VM_DB_USER}:{VM_DB_PASS}@{VM_DB_HOST}:{VM_DB_PORT}/{VM_DB_NAME}?ssl=false"
engine = create_engine(db_url)
print(f"[STEP 2] Successfully connected to database: {VM_DB_NAME}")


# --- 3) Create a DataFrame and write to a table ---
table_name = "visits"
df = pd.DataFrame(
    [
        {"patient_id": 1, "visit_date": "2025-09-01", "bp_sys": 118, "bp_dia": 76},
        {"patient_id": 2, "visit_date": "2025-09-02", "bp_sys": 130, "bp_dia": 85},
        {"patient_id": 3, "visit_date": "2025-09-03", "bp_sys": 121, "bp_dia": 79},
        {"patient_id": 4, "visit_date": "2025-09-04", "bp_sys": 110, "bp_dia": 70},
        {"patient_id": 5, "visit_date": "2025-09-05", "bp_sys": 125, "bp_dia": 82},
    ]
)

# Write the DataFrame to the database
# Removed unnecessary connect_args
df.to_sql(table_name, con=engine, if_exists="replace", index=False)
print(f"[STEP 3] Successfully wrote 5 records to table `{table_name}`.")


# --- 4) Read back a quick check ---
print("[STEP 4] Reading back row count to verify data...")
with engine.connect() as conn:
    count_df = pd.read_sql(f"SELECT COUNT(*) AS n_rows FROM `{table_name}`", con=conn)
print(count_df)