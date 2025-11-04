import os, requests

BOT = os.environ.get("TELEGRAM_BOT_TOKEN","")
CHAT = os.environ.get("TELEGRAM_CHAT_ID","")

def push_telegram(video_path, caption):
    if not BOT or not CHAT:
        print("Telegram not configured, skipping delivery.")
        return
    url = f"https://api.telegram.org/bot{BOT}/sendVideo"
    with open(video_path, "rb") as f:
        r = requests.post(url, data={"chat_id": CHAT, "caption": caption}, files={"video": f})
        try:
            r.raise_for_status()
        except Exception as e:
            print("Telegram send failed:", e)
