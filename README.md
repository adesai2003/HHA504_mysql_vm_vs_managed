# HHA504_mysql_vm_vs_managed

### Cloud Chosen and Region

* **Cloud Provider:** Google Cloud (GCP)
* **Region:** us-central1 (Iowa)

### Public High-Level Steps to Reproduce

1.  **VM Setup (Self-Managed):**
    * Created a Compute Engine VM (`e2-micro`, Ubuntu 22.04 LTS).
    * Created a custom GCP firewall rule to allow Ingress traffic on **TCP 3306** 
    * SSH'd into the VM, installed `mysql-server mysql-client`.
    * Edited `/etc/mysql/mysql.conf.d/mysqld.cnf` to change `bind-address = 127.0.0.1` to `bind-address = 0.0.0.0`.
    * Created the remote `class_user` with privileges.

2.  **Managed Setup (Cloud SQL):**
    * Created a Cloud SQL for MySQL instance (`db-f1-micro`, MySQL 8.0) with a **Public IP**.
    * Configured the **Authorized networks** list on the instance 
    * Created the non-default user `class_user` via the GCP Console.

3.  **Code Execution:**
    * Created and populated the local `.env` file with credentials and IPs.
    * Ran `pip install -r requirements.txt` (including `sqlalchemy`, `pymysql`, `pandas`, `python-dotenv`).
    * Executed `python scripts/vm_demo.py` and `python scripts/managed_demo.py`.

### Connection String Patterns

The SQLAlchemy connection uses the PyMySQL driver:
* **Pattern:** `mysql+pymysql://USER:PASS@HOST:PORT/DBNAME?ssl=false`

### Secrets Storage

Secrets are stored in a local, untracked file named **`.env`** at the root of the repository. The Python scripts use the `python-dotenv` package to load these variables into the environment at runtime, keeping them separate from the committed code. The `.gitignore` file explicitly ignores `.env`.

### Screenshots Summary and Links

* **screenshots/vm/**: VM creation page, Firewall rule, `systemctl status mysql` output, MySQL CLI session showing `SHOW DATABASES;`.
* **screenshots/managed/**: Cloud SQL instance Overview, Connection settings (Authorized networks), and Users list.


* **Video Link:** `<INSERT_YOUR_ZOOM/LOOM_LINK_HERE>`