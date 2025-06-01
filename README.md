# Cloudflare DDNS Python Script

Keep your Cloudflare DNS records automatically updated with your dynamic IP address using this straightforward DDNS script. Perfect for self-hosting enthusiasts!

## Features

* Automatically detects public IP address.
* Updates specified 'A' DNS records for multiple zones in Cloudflare.
* Compares current IP with the last known IP to avoid unnecessary API calls.
* Logs activity to both console and a log file.
* (Optional) Sends notifications via a custom PHP script, including system status like Apache and pending updates (Linux-specific).
* Configurable via a `config.py` file and environment variables.

## Prerequisites

* Python 3.6+
* `requests` Python library
* A Cloudflare account and API Token.
* Zone ID(s) for the domain(s) you want to update.
* (Optional) PHP installed and configured if using PHP notifications.
* (Optional, for system status in notifications) `systemctl` and `apt` (typically found on Debian/Ubuntu Linux).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/jaguarclaws2007/cloudflare-ddns.git
    cd cloudflare-ddns
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the Script:**
    * Copy the example configuration file:
        ```bash
        cp config.py.example config.py
        ```
    * Edit `config.py` with your details:
        * **`CLOUDFLARE_API_TOKEN_ENV_VAR`**: (Recommended) Set this to the name of an environment variable that holds your Cloudflare API Token (e.g., `CF_API_TOKEN`). Then, make sure to set that environment variable in your system:
            ```bash
            export CF_API_TOKEN="your-actual-cloudflare-api-token"
            ```
            To make it permanent, add this line to your shell's profile file (e.g., `.bashrc`, `.zshrc`).
        * **`CLOUDFLARE_API_TOKEN`**: Alternatively, you can paste your API token here directly, but this is less secure if `config.py` is ever exposed. The script prioritizes the environment variable if `CLOUDFLARE_API_TOKEN_ENV_VAR` is set.
        * **`ZONES`**: Add your domain(s) and their corresponding Cloudflare Zone IDs. You can find the Zone ID on the "Overview" page for your domain in the Cloudflare dashboard.
            ```python
            ZONES = {
                "yourdomain.com": "YOUR_CLOUDFLARE_ZONE_ID",
                "sub.yourdomain.com": "YOUR_CLOUDFLARE_ZONE_ID_IF_DIFFERENT_OR_SAME",
                # Add more zones as needed
            }
            ```
        * **`IP_FILE`**, **`LOG_FILE`**: Adjust paths if needed. Defaults are relative to the script's location.
        * **`PHP_SCRIPT_PATH`**: If you want to use PHP notifications, set the path to your PHP script. Otherwise, leave as `None`.
        * **`ENABLE_APACHE_STATUS_CHECK`**, **`ENABLE_SYSTEM_UPDATE_CHECK`**: Set to `True` if you use PHP notifications and want these Linux-specific checks included.

4.  **Set Script Permissions (if running directly):**
    ```bash
    chmod +x cloudflare_ddns.py
    ```
    (Replace `cloudflare_ddns.py` with the actual filename of your Python script).

## Usage

Run the script manually:

```bash
sudo python3 cloudflare_ddns.py
````

Or, if you made it executable:

```bash
sudo ./cloudflare_ddns.py
```

**Automate with Cron (Linux/macOS):**

To run the script periodically (e.g., every 15 minutes), open your crontab:

```bash
sudo crontab -e
```

Add a line like this (adjust path and timing as needed):

```cron
*/15 * * * * /usr/bin/python3 /path/to/cloudflare_ddns.py > /path/to/cron.log 2>&1
```

  * Ensure you use absolute paths in your cron job for the Python interpreter and the script.
  * The `> /path/to/cron.log 2>&1` part is optional but recommended for capturing any output or errors from the cron job itself (script's own logging will go to `LOG_FILE` defined in `config.py`).

  * Note: This will run every 15 minutes.

## DNS Record Configuration

  * This script updates existing **'A' records**. It does not create new ones. Ensure the 'A' records you want to update already exist in your Cloudflare DNS settings for the configured zones.
  * The script will update **all** 'A' records found in the specified zones to the new public IP. If you only want to update specific 'A' records (e.g., `home.example.com` but not `office.example.com`), you'll need to modify the script logic in the `main` function to filter records by `record_name`.
  * Updated records will have **Proxied** status set to **True** by default.

## Troubleshooting

  * **Check Logs:** The script logs to `cloudflare_ddns.log` (or your configured `LOG_FILE`) and the console. These logs are the first place to look for errors.
  * **API Token Permissions:** Ensure your Cloudflare API Token has the necessary permissions:
      * `Zone:Read`
      * `DNS:Edit` for all zones you want to update.
  * **Zone ID:** Double-check that your Zone IDs in `config.py` are correct.
  * **PHP Script Path:** If using PHP notifications, verify the `PHP_SCRIPT_PATH` is correct and the PHP script has execute permissions and is working independently.

## Contributing

Contributions are welcome\! Please feel free to submit a pull request or open an issue for bugs, feature requests, or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/jaguarclaws2007/cloudflare-ddns/blob/main/LICENSE) file for details.
