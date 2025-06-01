# send_ip_change_notification.py
import argparse
import os
import logging
from discord_notifier import DiscordNotifier # Ensure discord_notifier.py is in the same directory or in PYTHONPATH

# Configure basic logging for this script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
script_logger = logging.getLogger(__name__)

def main():
    # --- Configuration: Get Discord Webhook URL ---
    # Strongly recommended to set this as an environment variable
    webhook_url_env = os.getenv("DISCORD_WEBHOOK_URL_PYTHON") # Use a distinct name if you have other webhooks

    parser = argparse.ArgumentParser(description="Send a Discord notification about an IP address change.")
    parser.add_argument("new_ip", help="The new public IP address.")
    parser.add_argument("apache_status", help="Status of the Apache server (e.g., 'active', 'N/A').")
    parser.add_argument("update_status", help="Status of system updates (e.g., 'Updates Available', 'N/A').")
    parser.add_argument("system_time", help="Current system time (e.g., 'YYYY-MM-DD HH:MM:SS').")
    parser.add_argument("domain_status", help="A string describing the status of DNS updates for domains.")
    parser.add_argument(
        "--webhook-url",
        default=webhook_url_env,
        help="Discord Webhook URL. Overrides DISCORD_WEBHOOK_URL_PYTHON environment variable if provided."
    )

    args = parser.parse_args()

    if not args.webhook_url:
        script_logger.critical(
            "Discord webhook URL is not set. "
            "Please set the DISCORD_WEBHOOK_URL_PYTHON environment variable or use the --webhook-url argument."
        )
        print("Error: Discord webhook URL not configured.")
        exit(1)

    try:
        notifier = DiscordNotifier(webhook_url=args.webhook_url)
    except ValueError as e:
        script_logger.critical(f"Failed to initialize DiscordNotifier: {e}")
        print(f"Error: {e}")
        exit(1)

    # Customize the notification
    notifier.set_color("#a80000")  # A red shade, similar to your PHP
    notifier.set_title("URGENT: System IP Address Change Detected ")  # Title of the notification
    notifier.set_content(f"**Alert!** The server's public IP address has changed.") # Main text

    # Add fields
    notifier.add_field(name="New Public IP", value=args.new_ip, inline=True)
    notifier.add_field(name="System Time", value=args.system_time, inline=True)
    # Add a blank inline field if you want the next non-inline field to start on a new line clearly
    # notifier.add_field(name="\u200b", value="\u200b", inline=True) # Zero-width space

    notifier.add_field(name="Apache2 Status", value=args.apache_status, inline=False)
    notifier.add_field(name="System Updates", value=args.update_status, inline=False)

    # Format domain_status to be more readable, potentially in a code block
    # Ensure domain_status is not excessively long (Discord field value limit is 1024)
    domain_report = args.domain_status
    if len(domain_report) > 1000: # Leave some room for formatting
        domain_report = domain_report[:1000] + "..."
    
    notifier.add_field(name="DNS Update Status", value=f"```\n{domain_report}\n```", inline=False)

    if notifier.send():
        script_logger.info("IP change notification sent successfully via Python.")
        print("Notification sent successfully.")
    else:
        script_logger.error("Failed to send IP change notification via Python.")
        print("Error: Failed to send notification.")
        exit(1) # Exit with an error code

if __name__ == "__main__":
    main()