# managed_demo.py — Linear, step-by-step demo for managed MySQL (Azure/GCP/OCI)
#
# IMPORTANT: For managed services, the database must usually be created 
# manually by an administrator via the cloud console before running this script.
#
# Prereqs:
# pip install sqlalchemy pymysql pandas python-dotenv
#
# Env vars (populate a local .env):
# MAN_DB_HOST, MAN_DB_PORT, MAN_DB_USER, MAN_DB_PASS, MAN_DB_NAME

import os, time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- 0) Load environment ---
# IMPORTANT: Adjust this path to wherever your .env file is located if necessary
load_dotenv(".env")

MAN_DB_HOST = os.getenv("MAN_DB_HOST")
MAN_DB_PORT = os.getenv("MAN_DB_PORT", "3306")
MAN_DB_USER = os.getenv("MAN_DB_USER")
MAN_DB_PASS = os.getenv("MAN_DB_PASS")
MAN_DB_NAME = os.getenv("MAN_DB_NAME")

print("[ENV] MAN_DB_HOST:", MAN_DB_HOST)
print("[ENV] MAN_DB_PORT:", MAN_DB_PORT)
print("[ENV] MAN_DB_USER:", MAN_DB_USER)
print("[ENV] MAN_DB_NAME:", MAN_DB_NAME)

# Check if essential variables are loaded
if not all([MAN_DB_HOST, MAN_DB_USER, MAN_DB_PASS, MAN_DB_NAME]):
    print("\n[ERROR] Missing environment variables. Please check your .env file.")
    exit(1)

# --- 1) Connect directly to the target database ---
# NOTE: For managed services, we assume MAN_DB_NAME already exists and skip the 
# database creation step (which often fails due to permission restrictions).
t0 = time.time()

# Construct the full URL, omitting non-standard ?ssl=false parameter
db_url = f"mysql+pymysql://{MAN_DB_USER}:{MAN_DB_PASS}@{MAN_DB_HOST}:{MAN_DB_PORT}/{MAN_DB_NAME}"
masked_url = db_url
if MAN_DB_PASS:
    masked_url = db_url.replace(MAN_DB_PASS, "*****")

print(f"[STEP 1] Connecting to Managed MySQL database: {MAN_DB_NAME}")
print(f"         URL (masked): {masked_url}")

# Create the engine, connecting directly to the target database
engine = create_engine(db_url, pool_pre_ping=True)

try:
    # Attempt a simple connection check to verify access
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print(f"[OK] Successfully connected to database `{MAN_DB_NAME}`.")
except Exception as e:
    print(f"[ERROR] Failed to connect to the managed instance. Common causes:")
    print(f"        1. Database `{MAN_DB_NAME}` does not exist (must be created manually).")
    print(f"        2. Network firewall/IP whitelisting is blocking access.")
    print(f"        3. Incorrect credentials.")
    print(f"        Error details: {e}")
    # Dispose and exit if connection fails
    engine.dispose()
    exit(1)


# --- 2) Create a DataFrame and write to a table ---
table_name = "visits"
df = pd.DataFrame(
    [
        {"patient_id": 10, "visit_date": "2025-10-01", "bp_sys": 117, "bp_dia": 75},
        {"patient_id": 11, "visit_date": "2025-10-02", "bp_sys": 131, "bp_dia": 86},
        {"patient_id": 12, "visit_date": "2025-10-03", "bp_sys": 122, "bp_dia": 80},
        {"patient_id": 13, "visit_date": "2025-10-04", "bp_sys": 111, "bp_dia": 71},
        {"patient_id": 14, "visit_date": "2025-10-05", "bp_sys": 126, "bp_dia": 83},
    ]
)
print(f"[STEP 2] Writing {len(df)} rows to table: {table_name}")

# Use engine.begin() for automatic transaction management when writing data
with engine.begin() as conn:
    df.to_sql(table_name, con=conn, if_exists="replace", index=False)
print("[OK] Wrote DataFrame to table.")

# --- 3) Read back a quick check ---
print("[STEP 3] Reading back row count ...")
with engine.connect() as conn:
    count_df = pd.read_sql(f"SELECT COUNT(*) AS n_rows FROM `{table_name}`", con=conn)
print("Row count read successfully:")
print(count_df)

elapsed = time.time() - t0
print(f"\n[DONE] Managed path completed in {elapsed:.1f}s at {datetime.utcnow().isoformat()}Z")

