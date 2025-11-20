# vm_demo.py — Linear, step-by-step demo for self-managed MySQL on a VM
# Run this file top-to-bottom OR run it cell-by-cell in VS Code.
# Prereqs:
#   pip install sqlalchemy pymysql pandas python-dotenv
#
# Env vars (populate a local .env):
#   VM_DB_HOST, VM_DB_PORT, VM_DB_USER, VM_DB_PASS, VM_DB_NAME

import os, time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- 0) Load environment ---
# IMPORTANT: Adjust this path to wherever your .env file is located
load_dotenv(".env")

VM_DB_HOST = os.getenv("VM_DB_HOST")
VM_DB_PORT = os.getenv("VM_DB_PORT", "3306")
VM_DB_USER = os.getenv("VM_DB_USER")
VM_DB_PASS = os.getenv("VM_DB_PASS")
VM_DB_NAME = os.getenv("VM_DB_NAME")

print("[ENV] VM_DB_HOST:", VM_DB_HOST)
print("[ENV] VM_DB_PORT:", VM_DB_PORT)
print("[ENV] VM_DB_USER:", VM_DB_USER)
print("[ENV] VM_DB_NAME:", VM_DB_NAME)

# --- 1) Connect to server (no DB) and ensure database exists ---
t0 = time.time()

# 1.1) Construct the URL without any non-standard SSL parameters
# The database driver (pymysql) will default to no SSL if no configuration is provided.
server_url_no_db = f"mysql+pymysql://{VM_DB_USER}:{VM_DB_PASS}@{VM_DB_HOST}:{VM_DB_PORT}/"
masked_url = server_url_no_db
if VM_DB_PASS:
    masked_url = server_url_no_db.replace(VM_DB_PASS, "*****")
print("[STEP 1] Connecting to MySQL server (no DB):", masked_url)

# 1.2) Create the engine. We removed the incorrect connect_args.
engine_server = create_engine(
    server_url_no_db,
    pool_pre_ping=True
)

try:
    with engine_server.connect() as conn:
        # Create database command
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{VM_DB_NAME}`"))
        conn.commit()
    print(f"[OK] Ensured database `{VM_DB_NAME}` exists.")
except Exception as e:
    print(f"[ERROR] Failed to connect or create database. Check VM status and credentials: {e}")
    # Exit if connection fails here, as subsequent steps will fail too.
    exit(1)
finally:
    # Always dispose the engine to clean up connections
    engine_server.dispose()


# --- 2) Connect to the target database ---
# 2.1) Construct the target DB URL, also without non-standard SSL parameters
db_url = f"mysql+pymysql://{VM_DB_USER}:{VM_DB_PASS}@{VM_DB_HOST}:{VM_DB_PORT}/{VM_DB_NAME}"
engine = create_engine(db_url)
print(f"[STEP 2] Engine created for database: {VM_DB_NAME}")

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

# 3.1) Write the DataFrame. Removed the invalid connect_args argument.
print(f"[STEP 3] Writing {len(df)} rows to table `{table_name}`...")
df.to_sql(table_name, con=engine, if_exists="replace", index=False)
print(f"[OK] Table `{table_name}` created and populated.")

# --- 4) Read back a quick check ---
print("[STEP 4] Reading back row count ...")
try:
    with engine.connect() as conn:
        count_df = pd.read_sql(f"SELECT COUNT(*) AS n_rows FROM `{table_name}`", con=conn)
    print("Row count read successfully:")
    print(count_df)
except Exception as e:
    print(f"[ERROR] Failed to read from table: {e}")


elapsed = time.time() - t0
print(f"\n[DONE] VM path completed in {elapsed:.1f}s at {datetime.utcnow().isoformat()}Z")