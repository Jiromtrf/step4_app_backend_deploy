import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HEADERS = {"Authorization": f"Bearer {SLACK_TOKEN}"}

def get_user_info(user_id):
    """ユーザーIDからユーザー名を取得"""
    url = "https://slack.com/api/users.info"
    params = {"user": user_id}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200 and response.json().get("ok"):
        return response.json().get("user", {}).get("real_name", "Unknown User")
    return "Unknown User"

def send_message_to_slack(text):
    """Slackにメッセージを送信"""
    url = "https://slack.com/api/chat.postMessage"
    data = {"channel": CHANNEL_ID, "text": text}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def get_messages_from_slack():
    """Slackからメッセージ、投稿者名、リアクション情報を取得"""
    url = "https://slack.com/api/conversations.history"
    params = {"channel": CHANNEL_ID, "limit": 10}
    response = requests.get(url, headers=HEADERS, params=params)

    # Slack APIのレスポンス全体を出力して確認
    print("Slack API Response:", response.json())

    if response.status_code == 200 and response.json().get("ok"):
        messages = []
        for message in response.json().get("messages", []):
            user_id = message.get("user", "Unknown")
            user_name = get_user_info(user_id)
            reactions = message.get("reactions", [])

            # 各メッセージの情報を収集
            messages.append({
                "text": message.get("text", ""),
                "user": user_name,
                "reactions": [
                    {"name": reaction["name"], "count": reaction["count"]}
                    for reaction in reactions
                ]
            })
        return {"status": "ok", "data": messages}
    else:
        # エラー時の詳細メッセージを出力
        error_message = response.json().get("error", "Unknown error")
        print("Error:", error_message)
        return {"status": "error", "message": error_message}

def add_reaction_to_message(channel, timestamp, emoji):
    """メッセージにスタンプを追加"""
    url = "https://slack.com/api/reactions.add"
    data = {"channel": channel, "name": emoji, "timestamp": timestamp}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def reply_to_message(channel, thread_ts, text):
    """メッセージにスレッドで返信"""
    url = "https://slack.com/api/chat.postMessage"
    data = {"channel": channel, "text": text, "thread_ts": thread_ts}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()
