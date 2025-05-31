#!/usr/bin/env python3
# Cloudflare DDNS Update Script
# This script updates Cloudflare DNS 'A' records with the current public IP address.


import subprocess
import requests
import json
import datetime
import logging
import os

# --- Load Configuration ---
try:
    import config
except ImportError:
    print("CRITICAL: Configuration file 'config.py' not found.")
    print("Please copy 'config.py.example' to 'config.py' and fill in your details.")
    exit(1)

CLOUDFLARE_API_TOKEN = ""
if hasattr(config, 'CLOUDFLARE_API_TOKEN_ENV_VAR') and config.CLOUDFLARE_API_TOKEN_ENV_VAR:
    CLOUDFLARE_API_TOKEN = os.getenv(config.CLOUDFLARE_API_TOKEN_ENV_VAR)
if not CLOUDFLARE_API_TOKEN and hasattr(config, 'CLOUDFLARE_API_TOKEN'):
    CLOUDFLARE_API_TOKEN = config.CLOUDFLARE_API_TOKEN

if not CLOUDFLARE_API_TOKEN:
    print("CRITICAL: Cloudflare API Token not configured.")
    print("Please set it in config.py or via the environment variable specified in config.py.")
    exit(1)

ZONES = getattr(config, 'ZONES', {})
if not ZONES:
    print("CRITICAL: No ZONES configured in config.py. Exiting.")
    exit(1)

IP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), getattr(config, 'IP_FILE', 'cloudflare_ddns_currentIP.txt'))
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), getattr(config, 'LOG_FILE', 'cloudflare_ddns.log'))
PHP_SCRIPT_PATH = getattr(config, 'PHP_SCRIPT_PATH', None)
ENABLE_APACHE_STATUS_CHECK = getattr(config, 'ENABLE_APACHE_STATUS_CHECK', False)
ENABLE_SYSTEM_UPDATE_CHECK = getattr(config, 'ENABLE_SYSTEM_UPDATE_CHECK', False)
ENABLE_DISCORD_NOTIFICATIONS = getattr(config, 'ENABLE_DISCORD_NOTIFICATIONS', False)

# IMPORTANT: Keep your API token secure


def setup_logging():
    """Configures logging to file and console."""
    # Basic configuration for logging
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    console_handler.setLevel(logging.INFO) # Console shows INFO and above

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # Capture DEBUG and above for the file
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_public_ip():
    """Get current public IP address."""
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["ip"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error parsing IP address from response: {e}")
        return None

def get_dns_records(zone_id):
    """Retrieve all Cloudflare 'A' DNS records for a given zone."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data.get("result", [])
        else:
            logging.error(f"Cloudflare API error fetching DNS records for zone {zone_id}: {data.get('errors')}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error fetching DNS records for zone {zone_id}: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error fetching DNS records for zone {zone_id}: {e}")
        return []

def update_dns_record(zone_id, record_id, record_name, new_ip):
    """Update a specific Cloudflare DNS 'A' record. Sets proxied to True."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": record_name,
        "content": new_ip,
        "ttl": 1, # 1 for auto
        "proxied": True # Set proxied status to True as per original script's behavior
    }
    
    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_details = "Unknown error"
        try:
            error_details = e.response.json().get("errors", [{"message": str(e)}])
        except json.JSONDecodeError:
            error_details = e.response.text
        logging.error(f"HTTP error updating DNS record {record_name} ({record_id}): {e.response.status_code} - {error_details}")
        return {"success": False, "errors": [{"message": f"HTTP {e.response.status_code}: {error_details}"}]}
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error updating DNS record {record_name} ({record_id}): {e}")
        return {"success": False, "errors": [{"message": str(e)}]}

def save_current_ip(ip):
    """Save current IP to file."""
    try:
        with open(IP_FILE, "w") as file:
            file.write(ip)
        logging.info(f"Successfully saved current IP ({ip}) to {IP_FILE}")
    except IOError as e:
        logging.error(f"Error saving current IP to {IP_FILE}: {e}")

def load_last_ip():
    """Load the last saved IP from file."""
    try:
        with open(IP_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.info(f"IP file ({IP_FILE}) not found. Will assume IP needs update.")
        return None
    except IOError as e:
        logging.error(f"Error loading last IP from {IP_FILE}: {e}")
        return None

def check_apache_status():
    """Check Apache2 status."""
    try:
        result = subprocess.run(["systemctl", "is-active", "apache2"], capture_output=True, text=True, check=False)
        return result.stdout.strip()
    except Exception as e:
        logging.warning(f"Could not check Apache status: {e}")
        return "Unknown"

def check_system_updates():
    """Check for pending system updates."""
    try:
        result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True, check=False)
        # A more reliable check might be to count lines after the header "Listing... Done"
        if "upgradable" in result.stdout and len(result.stdout.splitlines()) > 1:
             return "Updates Available"
        return "Up-to-date"
    except Exception as e:
        logging.warning(f"Could not check system updates: {e}")
        return "Unknown"

def main():
    """Main function to check and update DDNS for all 'A' records in configured zones."""
    setup_logging() # Initialize logging
    
    logging.info("Starting DDNS update process...")
    current_ip = get_public_ip()
    if not current_ip:
        logging.error("Could not fetch public IP. Exiting.")
        # Optionally send a notification about failing to get public IP
        return

    last_ip = load_last_ip()
    if current_ip == last_ip:
        logging.info(f"IP unchanged ({current_ip}). No update needed.")
        # If you want to send a notification even when IP is unchanged, add it here.
        return

    logging.info(f"Public IP changed from '{last_ip}' to '{current_ip}'. Starting DNS updates.")

    apache_status = "N/A"
    update_status = "N/A"
    system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    overall_script_success = True # Tracks if all operations (including updates) were successful
    any_record_updated_successfully = False
    domain_statuses_messages = []

    for zone_name, zone_id in ZONES.items():
        logging.info(f"Processing zone: {zone_name} (ID: {zone_id})")
        all_a_records = get_dns_records(zone_id)

        if not all_a_records:
            message = f"Zone '{zone_name}': No 'A' records found or error fetching records."
            logging.warning(message)
            domain_statuses_messages.append(message)
            # Not necessarily a script failure if a zone has no 'A' records.
            continue
        
        zone_update_summary = []
        records_in_zone_to_update = 0
        records_in_zone_updated_successfully = 0

        for record in all_a_records:
            record_id = record.get("id")
            record_name = record.get("name")
            record_content_ip = record.get("content")

            if not all([record_id, record_name, record_content_ip]):
                logging.warning(f"Skipping malformed record in zone {zone_name}: {record}")
                continue

            if record_content_ip == current_ip:
                logging.info(f"Record '{record_name}' in zone '{zone_name}' already points to {current_ip}. No update needed.")
                # zone_update_summary.append(f"{record_name}: Already {current_ip}") # Optional: for very verbose notifications
                continue
            
            records_in_zone_to_update += 1
            logging.info(f"Updating record '{record_name}' (ID: {record_id}) in zone '{zone_name}' from {record_content_ip} to {current_ip}")
            update_response = update_dns_record(zone_id, record_id, record_name, current_ip)
            
            if update_response and update_response.get("success"):
                logging.info(f"Successfully updated '{record_name}' to {current_ip}.")
                zone_update_summary.append(f"Updated {record_name} to {current_ip} (Proxied: ✅)")
                any_record_updated_successfully = True
                records_in_zone_updated_successfully +=1
            else:
                error_msg = "Unknown error"
                if update_response and update_response.get("errors"):
                    error_msg = update_response["errors"][0].get("message", "Unknown error")
                logging.error(f"Failed to update '{record_name}': {error_msg}. Full response: {update_response}")
                zone_update_summary.append(f"Failed to update {record_name}: {error_msg}")
                overall_script_success = False # Mark failure if any update fails

        if zone_update_summary: # Add summary for the zone if there was anything to report
            domain_statuses_messages.append(f"--- Zone: {zone_name} ---")
            domain_statuses_messages.extend(zone_update_summary)
        elif records_in_zone_to_update == 0 and all_a_records: # All records were already up-to-date
             domain_statuses_messages.append(f"Zone '{zone_name}': All 'A' records already up-to-date.")

    if PHP_SCRIPT_PATH:
        if ENABLE_APACHE_STATUS_CHECK:
            apache_status = check_apache_status()
        if ENABLE_SYSTEM_UPDATE_CHECK:
            update_status = check_system_updates()

    # Send Discord notification
    if domain_statuses_messages: # Only send if there are messages (updates, errors, or zone info)
        domain_status_report = "\n".join(domain_statuses_messages)
        logging.info("Sending notification via PHP script...")
        try:
            if ENABLE_DISCORD_NOTIFICATIONS:
                php_process = subprocess.run(
                    ['php', PHP_SCRIPT_PATH, current_ip, apache_status, update_status, system_time, domain_status_report],
                    capture_output=True, text=True, check=True, timeout=30 # Added timeout and check
                )
                logging.info(f"PHP script executed successfully. Output: {php_process.stdout.strip()}")
            else:
                logging.info("PHP script notifications are disabled (ENABLE_DISCORD_NOTIFICATIONS is False).")
        except subprocess.CalledProcessError as e:
            logging.error(f"PHP script execution failed. Return code: {e.returncode}")
            logging.error(f"PHP script stdout: {e.stdout.strip()}")
            logging.error(f"PHP script stderr: {e.stderr.strip()}")
            overall_script_success = False # Notification failure is a script failure
        except subprocess.TimeoutExpired:
            logging.error(f"PHP script timed out after 30 seconds.")
            overall_script_success = False
        except FileNotFoundError:
            logging.error(f"PHP script not found at {PHP_SCRIPT_PATH}")
            overall_script_success = False
        except Exception as e:
            logging.error(f"An unexpected error occurred while running PHP script: {e}")
            overall_script_success = False
    else:
        # This case means IP changed, but no records needed update AND no zones had errors during fetch.
        # (e.g. all records in all zones were already correct, or no 'A' records in any zones)
        logging.info("IP changed, but no specific DNS record updates or errors to report for notifications.")
        # We might still want to send a generic "IP changed to X, all records checked" notification.
        # For now, it sends nothing if domain_statuses_messages is empty.
        # A basic notification could be constructed here if needed.
        pass


    if overall_script_success and current_ip != last_ip: # IP changed and all operations were successful
        logging.info(f"All operations completed successfully. New IP is {current_ip}.")
        save_current_ip(current_ip)
        if not any_record_updated_successfully:
            logging.info("Note: Although IP changed, no records required an update (e.g., already correct, or no relevant 'A' records found). IP file updated.")
    elif not overall_script_success and current_ip != last_ip:
        logging.error("One or more operations failed during the DDNS update process. New IP was not saved to allow re-attempt on next run.")
    
    logging.info("DDNS update process finished.")

if __name__ == "__main__":
    main()
