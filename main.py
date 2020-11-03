#! /usr/bin/python3

import os
import subprocess
from datetime import datetime

import requests

from html_parser import CoronaNewsParser


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
    response_text = response.text.replace(">", ">\n")

    # Parse HTML and only read content from main tag
    parser = CoronaNewsParser()
    parser.feed(response_text)
    new_response = parser.get_data()

    # Read previous version
    try:
        with open(f"{project_dir}/{file_key}.html", "r") as file:
            old_response = file.read()
    except FileNotFoundError:
        # File didn't exist until now, no comparison possible. Create the file and return
        with open(f"{project_dir}/{file_key}.html", "w") as file:
            file.writelines(new_response)
        with open(f"{project_dir}/log.txt", "a") as log:
            log.write(f"{datetime.now()} - {file_key}: Initializing new HTML file for {file_key}\n")
        return

    # No updates? Log and exit
    if old_response == new_response:
        with open(f"{project_dir}/log.txt", "a") as log:
            log.write(f"{datetime.now()} - {file_key}: No changes detected\n")
        return

    # Get diff using diff-command
    diff_result = subprocess.run(["diff", f"{project_dir}/{file_key}.html", "-"],
                                 stdout=subprocess.PIPE, input=new_response, encoding="utf-8")
    decoded_diff_result = diff_result.stdout

    # Log result
    with open(f"{project_dir}/log.txt", "a") as log:
        log.write(f"{datetime.now()} - {file_key}: {decoded_diff_result}\n")

    # Update saved HTML file
    with open(f"{project_dir}/{file_key}.html", "w") as file:
        file.writelines(new_response)

    # Send update to Slack webhook
    with open('webhook_url.txt', 'r') as file:
        webhook_url = file.read().replace('\n', '')
    message = {"text": f"*{message_title}*\n{decoded_diff_result}"}
    requests.post(webhook_url, json=message)


check_updates("https://www.htw-berlin.de/coronavirus/faq-fuer-studierende/", "Studierenden-FAQ-Update", "studi")
check_updates("https://www.htw-berlin.de/coronavirus/faq-fuer-lehrende/", "Lehrenden-FAQ-Update", "lehrende")
