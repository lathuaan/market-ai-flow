
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/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"
    requests.post(webhook_url, json={"text": message})
