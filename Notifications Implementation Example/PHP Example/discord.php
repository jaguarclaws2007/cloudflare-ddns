<?php
class DiscordNotification {
    private $webhook_url;
    private $color;
    private $title;
    private $content = "New form submission!";
    private $fields = [];

    public function __construct() {
        $this->webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL";
        $this->color = 0x000000; // Default color (black)
    }

    public function setColor($hexColor) {
		if (preg_match('/^#[0-9A-Fa-f]{6}$/', $hexColor)) {
            $decimalColor = hexdec(substr($hexColor, 1));
            $this->color = $decimalColor;
        } else {
            error_log("Invalid hex color format: $hexColor. Using default color.");
            $this->color = 0x000000;
        }
    }

    public function setTitle($title) {
        $this->title = $title;
    }
	
	public function setContent($text) {
        $this->content = $text;
    }

    public function addField($name, $value, $inline = false) {
        $this->fields[] = [
            'name' => $name,
            'value' => $value,
            'inline' => $inline
        ];
    }

    public function send() {
        $payload = json_encode([
            'content' => $this->content,
            'embeds' => [
                [
                    'title' => $this->title,
                    'color' => $this->color,
                    'fields' => $this->fields
                ]
            ]
        ]);

        $ch = curl_init($this->webhook_url);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        $response = curl_exec($ch);
        curl_close($ch);

        if ($response === false) {
            error_log('Error sending notification to Discord');
        }
    }
}

?>
