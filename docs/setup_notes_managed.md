* **Name:** 
* **Region/Zone:** us-central1 (Single Zone)
* **Database Version:** MySQL 8.0
* **Machine Type:** db-f1-micro (Shared-core, 0.6 GB RAM)
* **Storage:** 10 GB SSD (Enabled auto-storage increase)
* **Initial Admin:** `root` (created automatically with specified password)
* **Backups/HA:** Enabled automated daily backups. Disabled High Availability (HA) for lower cost.

## Ordered Execution Steps

1.  **Create Instance:** Navigated to **Cloud SQL** -> **Create instance** -> **MySQL**. Specified instance ID, root password, region, and machine type.
2.  **Enable Public IP:** Under **Configuration options** -> **Connectivity**:
    * Selected **Public IP**.
3.  **Authorize Networks (CRITICAL STEP):** In the same **Connectivity** section, under **Authorized networks**:
    * Clicked **Add network**.
    * Set the IP range to my local machine's public IP in CIDR notation. This acts as the firewall for the managed service.
4.  **Create Application User:** After the instance was created, navigated to the **Users** tab:
    * Clicked **Create user**.
    * Set **User name** to `aaravdba` and **Password** to `aaravdba03`.

5.  **Final Test:** Retrieved the **Public IP address** from the Overview tab and ran `managed_demo.py` locally.

## Troubles and Solutions

* **Trouble:** Connection refused when running `managed_demo.py`.
* **Cause:** My home router's public IP address changed, or I forgot to specify the `/32` CIDR notation for my single IP address.
* **Solution:** Checked my public IP (via Google search), navigated back to the **Connections** -> **Networking** tab, and updated the IP range in the **Authorized networks** list to the correct `<NEW_IP_ADDRESS>/32`. Saved the change and re-ran the script.

