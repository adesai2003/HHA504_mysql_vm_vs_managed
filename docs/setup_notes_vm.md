**Instance Details:**
* **Name:**  mysql-vm-club
* **Region/Zone:** us-central1
* **Machine Type:** e2-micro (1 vCPU, 1 GB RAM)
* **OS:** Ubuntu 22.04 LTS

## Ordered Execution Steps

1.  **Provision VM:** Created the Compute Engine instance. Used Network Tag `allow-3306` for later firewall application.
2.  **Firewall Rule:** Navigated to **VPC Network** -> **Firewall** and created a rule:
    * **Name:** `connect-mysql-allow`
    * **Direction:** Ingress
    * **Targets:** Specified Network Tag `3306`
    * **Source IP ranges:** `0.0.0.0/0` for initial testing
    * **Protocols/ports:** `tcp:3306`
3.  **SSH and Update:** Used the GCP Console's browser SSH feature.
    `
    sudo apt update
    sudo apt install mysql-server mysql-client -y
    ```
4.  **Configure Remote Access (CRITICAL STEP):** MySQL defaults to only listening on the local loopback address (127.0.0.1). This must be changed to allow connections from the host's public IP.
    ```bash
    sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
    ```
    **Edited Line:**
    ```conf
    # Find this line:
    # bind-address = 127.0.0.1
    # Change to:
    bind-address = 0.0.0.0
    ```
6.  **Restart Service:** Applied the configuration change.
    ```bash
    sudo systemctl restart mysql
    sudo systemctl status mysql
    ```
7.  **Create Remote User:** Connected to the local MySQL prompt as root to create the user for the Python scripts.
    ```sql
    sudo mysql -u root -p
    # Enter root password

    CREATE USER 'class_user'@'%' IDENTIFIED BY 'aaravdba';
    -- The '%' host allows connections from any external IP (restricted by GCP firewall)
    GRANT ALL PRIVILEGES ON *.* to 'aaravdba'@'%' WITH GRANT OPTION;


## Troubles and Solutions

* **Trouble:** Connection timed out when running `vm_demo.py` locally.
* **Cause:** The `bind-address` was still set to `127.0.0.1` inside `mysqld.cnf`, meaning the service was only listening for connections *inside the VM* itself, ignoring the public IP.
* **Solution:** Edited `/etc/mysql/mysql.conf.d/mysqld.cnf` to set `bind-address = 0.0.0.0` and ran `sudo systemctl restart mysql`.

