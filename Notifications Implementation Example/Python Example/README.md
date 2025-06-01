# PHP Discord Notification System for IP Changes

This PHP-based system sends notifications to a Discord channel via a webhook when triggered, typically by an IP address change event. It's designed to work with the Cloudflare DDNS Python script to provide real-time alerts.

## Features

* Sends formatted embed messages to Discord.
* Customizable message title, color, and content.
* Includes fields for new IP, service status (e.g., Apache), system update status, system time, and domain update details.
* Reusable `DiscordNotifier` class for other python projects.

## File Structure

It's recommended to place these files in a dedicated directory, for example, `notifications/py/`:

```
/path/to/your/scripts/
├── DiscordNotifier.py    # Core class for sending Discord webhook messages
└── send_ip_change_notification.py    # Script to format and send IP change specific notifications
```

## Prerequisites

* Python (tested with py 3.6+)
* Python requests extension installed (`pip install requests` or `pip install -r requirements.txt`).
* A Discord server where you have permissions to create a webhook.

## Setup

1.  **Place Files:**
    Ensure both `DiscordNotifier.py` and `send_ip_change_notification.py` are on your server, preferably in the same directory or in a location accessible by your PY environment.

2.  **Configure Discord Webhook URL:**
    * Open `config.py`.
    * Locate the following line:
        ```py
        DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
        ```
    * **Replace `"https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"` with your webhook URL**
        * To get a webhook URL: Go to your Discord Server Settings -> Integrations -> Webhooks -> New Webhook. Copy the Webhook URL.
    * Save the file.
    * Note: You can also save it as an enviermental variable. Just make sure to set the name in config.py (`DISCORD_API_WEBHOOK_URL_ENV_VAR = "ENV_VAR_NAME"`)

3.  **Verify Path in `send_ip_change_notification.py`:**
    * Open `send_ip_change_notification.py`.
    * Check the `from /path/to/discord_notifier import DiscordNotifier` line:
        ```py
        from /path/to/discord_notifier import DiscordNotifier; # Adjust the path as necessary
        ```
    * **Adjust `/path/to/your/DiscordNotifier.py`** to the correct absolute path to your `DiscordNotifier.py` file.
        * If both files are in the same directory, you can often use:
            ```py
            from discord_notifier import DiscordNotifier
            ```
    * Save the file.

## Usage

The `send_ip_change_notification.py` script is designed to be called from the command line, typically by another script (like the Python DDNS updater).

**Command Line Arguments:**

The script expects 5 arguments in the following order:

1.  `new_ip`: The new public IP address.
2.  `apache_status`: Status of the Apache server (e.g., "active", "inactive", "N/A").
3.  `update_status`: Status of system updates (e.g., "Updates Available", "Up-to-date", "N/A").
4.  `system_time`: Current system time (e.g., "YYYY-MM-DD HH:MM:SS").
5.  `domain_status`: A string describing the status of DNS updates for domains (can be multi-line, ensure it's passed as a single argument, often quoted).

**Example Command:**

```bash
/usr/bin/python3 /path/to/your/send_ip_change_notification.py "192.168.1.100" "active" "Updates Available" "2025-05-31 17:00:00" "Zone example.com: Updated home.example.com to 192.168.1.100"
```

* Make sure to use the correct path to your `py` executable and the `send_ip_change_notification.py` script.
* When passing the `domain_status` (argument 5), especially if it contains spaces or newlines, it's crucial to enclose it in quotes. The Python script calling this should handle this quoting.

## Customization

* **Notification Color & Title:** You can change the default color and title directly in `send_ip_change_notification.py`:
    ```py
    notifier.setColor("#a80000"); // Default red shade
    notifier.setTitle("URGENT!!! - System - IP address Change ");
    notifier.setContent("The public IP address of your server has changed...");
    ```
* **Fields:** Add, remove, or modify fields within `send_ip_change_notification.py` using the `notifier.addField()` method.

## Integration with Cloudflare DDNS Python Script

This PHP notification system is intended to be called by the `cloudflare-ddns.py` script (or similar). In the Python script's configuration (`config.py`):

1.  Set `PHP_SCRIPT_PATH` to the full path of `send_ip_change_notification.py`.
    ```python
    # In config.py
    ENABLE_DISCORD_NOTIFICATIONS = True
    DISCORD_SCRIPT_PATH = "/path/to/your/send_ip_change_notification.py"
    ```
2.  Ensure the Python script passes the arguments in the correct order as detailed in the "Usage" section above. The Python script handles collecting the IP, Apache status, etc., and then calls this PHP script via `subprocess.run()`.