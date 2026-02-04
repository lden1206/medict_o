from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# Load dictionary
with open("medictdata_o.json", "r", encoding="utf-8") as f:
    DICT = json.load(f)

ZALO_TOKEN = os.getenv("ZALO_TOKEN")  # set trên Render

def normalize(text):
    return text.strip().lower()

@app.route("/", methods=["GET"])
def home():
    return "ME Dictionary Zalo Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("DATA FROM ZALO:", data)

    message = data.get("message")
    if not message:
        return jsonify({"status": "ignored"}), 200

    user_text = message.get("text")
    user_id = message.get("from", {}).get("id")

    if not user_text or not user_id:
        return jsonify({"status": "ignored"}), 200

    key = normalize(user_text)
    found_key = None
    item = None

    if key in DICT:
        item = DICT[key]
        found_key = key
    else:
        for k in DICT:
            if key in k:
                item = DICT[k]
                found_key = k
                break

    if item:
        reply = (
            f"🔤 {found_key}\n"
            f"{item.get('ipa', '')}\n"
            f"🇻🇳 {item.get('meaning_vi', '')}\n\n"
            f"📘 {item.get('example_en', '')}\n"
            f"📙 {item.get('example_vi', '')}\n"
            f"📚 {item.get('book', '')} – Lesson {item.get('lesson', '')}"
        )
    else:
        reply = f"❌ Không tìm thấy từ: {user_text}"

    send_zalo_message(user_id, reply)
    return jsonify({"status": "ok"}), 200

def send_zalo_message(user_id, text):
    url = "https://openapi.zalo.me/v3.0/oa/message/cs"

    headers = {
        "Content-Type": "application/json",
        "access_token": ZALO_TOKEN
    }

    payload = {
        "recipient": {
            "user_id": user_id
        },
        "message": {
            "text": text
        }
    }

    r = requests.post(url, headers=headers, json=payload)

    print("STATUS CODE:", r.status_code)
    print("SEND RESULT:", r.text)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




