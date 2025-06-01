# PHP Discord Notification System for IP Changes

This PHP-based system sends notifications to a Discord channel via a webhook when triggered, typically by an IP address change event. It's designed to work with the Cloudflare DDNS Python script to provide real-time alerts.

## Features

* Sends formatted embed messages to Discord.
* Customizable message title, color, and content.
* Includes fields for new IP, service status (e.g., Apache), system update status, system time, and domain update details.
* Reusable `DiscordNotification` class for other PHP projects.

## File Structure

It's recommended to place these files in a dedicated directory, for example, `notifications/php/`:

```
/path/to/your/scripts/
├── discord.php             # Core class for sending Discord webhook messages
└── notify-ip-change.php    # Script to format and send IP change specific notifications
```

## Prerequisites

* PHP (tested with PHP 7.x, 8.x)
* PHP cURL extension enabled (`php-curl` or `php<version>-curl`).
* A Discord server where you have permissions to create a webhook.

## Setup

1.  **Place Files:**
    Ensure both `discord.php` and `notify-ip-change.php` are on your server, preferably in the same directory or in a location accessible by your PHP environment.

2.  **Configure Discord Webhook URL:**
    * Open `discord.php`.
    * Locate the following line:
        ```php
        private $webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL";
        ```
    * **Replace `"https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"` with your actual Discord webhook URL.**
        * To get a webhook URL: Go to your Discord Server Settings -> Integrations -> Webhooks -> New Webhook. Copy the Webhook URL.
    * Save the file.

3.  **Verify Path in `notify-ip-change.php`:**
    * Open `notify-ip-change.php`.
    * Check the `require_once` line:
        ```php
        require_once '/path/to/your/discord.php'; // Adjust the path as necessary
        ```
    * **Adjust `/path/to/your/discord.php`** to the correct absolute path to your `discord.php` file.
        * If both files are in the same directory, you can often use:
            ```php
            require_once __DIR__ . '/discord.php';
            ```
    * Save the file.

## Usage

The `notify-ip-change.php` script is designed to be called from the command line, typically by another script (like the Python DDNS updater).

**Command Line Arguments:**

The script expects 5 arguments in the following order:

1.  `new_ip`: The new public IP address.
2.  `apache_status`: Status of the Apache server (e.g., "active", "inactive", "N/A").
3.  `update_status`: Status of system updates (e.g., "Updates Available", "Up-to-date", "N/A").
4.  `system_time`: Current system time (e.g., "YYYY-MM-DD HH:MM:SS").
5.  `domain_status`: A string describing the status of DNS updates for domains (can be multi-line, ensure it's passed as a single argument, often quoted).

**Example Command:**

```bash
php /path/to/your/notify-ip-change.php "192.168.1.100" "active" "Updates Available" "2025-05-31 17:00:00" "Zone example.com: Updated home.example.com to 192.168.1.100"
```

* Make sure to use the correct path to your `php` executable and the `notify-ip-change.php` script.
* When passing the `domain_status` (argument 5), especially if it contains spaces or newlines, it's crucial to enclose it in quotes. The Python script calling this should handle this quoting.

## Customization

* **Notification Color & Title:** You can change the default color and title directly in `notify-ip-change.php`:
    ```php
    $n->setColor("#a80000"); // Default red shade
    $n->setTitle("URGENT!!! - System - IP address Change ");
    $n->setContent("The public IP address of your server has changed...");
    ```
* **Fields:** Add, remove, or modify fields within `notify-ip-change.php` using the `$n->addField()` method.

## Integration with Cloudflare DDNS Python Script

This PHP notification system is intended to be called by the `cloudflare-ddns.py` script (or similar). In the Python script's configuration (`config.py`):

1.  Set `PHP_SCRIPT_PATH` to the full path of `notify-ip-change.php`.
    ```python
    # In config.py
    ENABLE_DISCORD_NOTIFICATIONS = True
    DISCORD_SCRIPT_PATH = "/path/to/your/notify-ip-change.php"

    ```
2.  Ensure the Python script passes the arguments in the correct order as detailed in the "Usage" section above. The Python script handles collecting the IP, Apache status, etc., and then calls this PHP script via `subprocess.run()`.