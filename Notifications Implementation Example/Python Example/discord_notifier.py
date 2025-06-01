# discord_notifier.py
import requests
import json
import logging

# Configure basic logging for this module
logger = logging.getLogger(__name__)
# You might want to configure logging more globally if this is part of a larger app
# For standalone use, if no other logging is set up, messages might not appear without:
# logging.basicConfig(level=logging.INFO)


class DiscordNotifier:
    """
    A class to send notifications to a Discord webhook.
    """
    def __init__(self, webhook_url: str):
        """
        Initializes the DiscordNotifier.

        :param webhook_url: The Discord webhook URL.
        """
        if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValueError("Invalid Discord webhook URL provided.")
        self.webhook_url = webhook_url
        self._color = 0x000000  # Default black
        self._title = None
        self._content = None # Main message content (outside embed)
        self._fields = []

    def set_color(self, hex_color: str):
        """
        Sets the color for the embed.

        :param hex_color: Color in hexadecimal format (e.g., "#RRGGBB").
        """
        if isinstance(hex_color, str) and hex_color.startswith("#") and len(hex_color) == 7:
            try:
                self._color = int(hex_color[1:], 16)
            except ValueError:
                logger.error(f"Invalid hex color format: {hex_color}. Using default color.")
                self._color = 0x000000
        elif isinstance(hex_color, int): # Allow direct decimal color
            self._color = hex_color
        else:
            logger.warning(f"Invalid color input: {hex_color}. Using default color 0x000000.")
            self._color = 0x000000

    def set_title(self, title: str):
        """
        Sets the title for the embed.

        :param title: The title text.
        """
        self._title = title

    def set_content(self, text: str):
        """
        Sets the main content of the message (this appears outside the embed).

        :param text: The main message text.
        """
        self._content = text

    def add_field(self, name: str, value: str, inline: bool = False):
        """
        Adds a field to the embed.

        :param name: The name of the field.
        :param value: The value of the field.
        :param inline: Whether the field should be displayed inline (default False).
                       Max 3 inline fields per row.
        """
        if not name or not value:
            logger.warning("Field name or value cannot be empty. Skipping field.")
            return
        if len(name) > 256:
            logger.warning(f"Field name '{name[:20]}...' is too long (max 256 chars). Truncating.")
            name = name[:256]
        if len(value) > 1024:
            logger.warning(f"Field value for '{name}' starting with '{value[:20]}...' is too long (max 1024 chars). Truncating.")
            value = value[:1024]

        self._fields.append({
            'name': name,
            'value': value,
            'inline': inline
        })

    def send(self) -> bool:
        """
        Sends the notification to Discord.

        :return: True if the message was sent successfully, False otherwise.
        """
        payload_embeds = []
        embed_data = {}

        if self._title:
            embed_data['title'] = self._title
        
        embed_data['color'] = self._color # Color is always set, defaults to black

        if self._fields:
            embed_data['fields'] = self._fields
        
        # An embed must have at least one of: title, description, fields, author, footer, image, thumbnail.
        # If only color is set, it might not be a valid embed.
        # We'll only add the embed to the payload if it has a title or fields.
        if embed_data.get('title') or embed_data.get('fields'):
            payload_embeds.append(embed_data)

        payload = {}
        if self._content:
            payload['content'] = self._content
        
        if payload_embeds:
            payload['embeds'] = payload_embeds
        
        if not payload.get('content') and not payload.get('embeds'):
            logger.error("Cannot send an empty message (no content and no valid embed data).")
            return False

        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            logger.info(f"Discord notification sent successfully. Status: {response.status_code}")
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error sending Discord notification: {e}")
            logger.error(f"Response status: {e.response.status_code}, Response content: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Discord notification: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return False