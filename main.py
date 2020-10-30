#! /usr/bin/python3

import subprocess
import requests
from datetime import datetime
import os


def check_updates(url, message_title, file_key):
    project_dir = os.path.dirname(__file__)

    # Fetch HTML from website
    response = requests.get(url)

    # Response not 200? Log error and exit
    if not response.ok:
        with open(f"{project_dir}/log.txt", "a") as log:
            log.write(f"{datetime.now()} - {file_key}: HTTP Error {response.status_code}\n")
            log.write(f"{response.text}\n")
        return

    # Add newlines after closing tags for better diff results
    new_response = response.text.replace(">", ">\n")

    # Read previous version
    with open(f"{project_dir}/{file_key}_new.html", "r") as file:
        old_response = file.read()

    # No updates? Log and exit
    if old_response == new_response:
        with open(f"{project_dir}/log.txt", "a") as log:
            log.write(f"{datetime.now()} - {file_key}: No changes detected\n")
        return

    # Save previous version as old and current version as new
    with open(f"{project_dir}/{file_key}_old.html", "w") as old:
        with open(f"{project_dir}/{file_key}_new.html", "w") as new:
            old.writelines(old_response)
            new.writelines(new_response)

    # Get diff using diff-command
    diff_result = subprocess.Popen(["diff", f"{project_dir}/{file_key}_old.html", f"{project_dir}/{file_key}_new.html"], stdout=subprocess.PIPE)
    decoded_diff_result = diff_result.stdout.read().decode("utf-8")

    # Log result
    with open(f"{project_dir}/log.txt", "a") as log:
        log.write(f"{datetime.now()} - {file_key}: {decoded_diff_result}\n")

    # Send update to Slack webhook
    with open('webhook_url.txt', 'r') as file:
        webhook_url = file.read().replace('\n', '')
    message = {"text": f"*{message_title}*\n{decoded_diff_result}"}
    requests.post(webhook_url, json=message)


check_updates("https://www.htw-berlin.de/coronavirus/faq-fuer-studierende/", "Studierenden-FAQ-Update", "studi")
check_updates("https://www.htw-berlin.de/coronavirus/faq-fuer-lehrende/", "Lehrenden-FAQ-Update", "lehrende")
