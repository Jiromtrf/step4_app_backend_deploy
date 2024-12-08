import os
import requests
from fastapi import Request
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
TARGET_USER_ID = "U12345678"
HEADERS = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

def add_reaction(channel, timestamp):
    url = "https://slack.com/api/reactions.add"
    data = {"channel": channel, "name": "thumbsup", "timestamp": timestamp}
    requests.post(url, headers=HEADERS, json=data)

def post_reply(channel, thread_ts):
    url = "https://slack.com/api/chat.postMessage"
    data = {"channel": channel, "text": "Thank you for your message!", "thread_ts": thread_ts}
    requests.post(url, headers=HEADERS, json=data)

async def slack_events(request: Request):
    payload = await request.json()
    event = payload.get("event", {})

    if event.get("type") == "message" and event.get("user") == TARGET_USER_ID:
        channel = event["channel"]
        timestamp = event["ts"]

        add_reaction(channel, timestamp)
        post_reply(channel, timestamp)

    return {"status": "ok"}
