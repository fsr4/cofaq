# HTW FAQ Updates
Checks the HTW Corona FAQ for updates and sends the diff to a Slack webhook

Usage: Run as crontab, e.g.
```
0 * * * * /home/user/htw-corona-updates/main.py
```
The script looks for a webhook.txt to load the webhook URL from, so you have to create this file in the project directory and add your custom Slack webhook URL as the only line to it.
