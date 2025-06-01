<?php
require_once '/path/to/your/discord.php'; // Adjust the path as necessary

if ($argc < 5) {
    echo "Usage: php /path/to/notify-ip-change.php <new_ip> <apache_status> <update_status> <system_time> <domain_status>\n";
    exit(1);
}

$newIP = $argv[1];
$apacheStatus = $argv[2];
$updateStatus = $argv[3];
$systemTime = $argv[4];
$domainStatus = $argv[5];

$n = new DiscordNotification();
$n->setColor("#a80000"); // Set the color to a red shade for urgency
if (!preg_match('/^#[0-9A-Fa-f]{6}$/i', $n->getColor())) {
    error_log("Invalid hex color format. Using default color.");
    $n->setColor("#000000"); // Default to black if the color is invalid
}
$n->setTitle("URGENT!!! - System - IP address Change "); // Set the title of the notification
$n->setContent("The public IP address of your server has changed. Here is the relevant info:"); 

$n->addField('New IP', $newIP); 
$n->addField('Apache2 Status', $apacheStatus); 
$n->addField('System Updates', $updateStatus);
$n->addField('System Time', $systemTime);
$n->addField('Domain Status', $domainStatus);

$n->send();
?>
