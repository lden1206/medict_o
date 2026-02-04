from flask import Flask, request, jsonify
import json
import re
import os

app = Flask(__name__)
@app.route("/", methods=["GET"])
def home():
    return "SERVER OK"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
fpath = os.path.join(BASE_DIR, "medictdata_o.json")

with open(fpath, "r", encoding="utf-8") as f:
    dictionary = json.load(f)

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s’']", "", text)  # giữ dấu '
    return re.sub(r"\s+", " ", text).strip()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("DATA FROM ZALO:", data)

    if "message" not in data:
        return jsonify({"text": "ℹ️ Event hệ thống, chưa có tin nhắn"})

    message = data.get("message", {})
    user_text = message.get("text")

    if not user_text:
        return jsonify({"text": "❌ Tin nhắn không phải dạng text"})

    key = normalize(user_text)

    if key in dictionary:
        item = dictionary[key]
        reply = (
            f"🔤 {key}\n"
            f"{item.get('ipa', '')}\n\n"
            f"🇻🇳 {item.get('meaning_vi', '')}\n\n"
            f"📘 {item.get('example_en', '')}\n"
            f"📙 {item.get('example_vi', '')}\n"
            f"📚 {item.get('book', '')} – Lesson {item.get('lesson', '')}"
        )
    else:
        reply = f"❌ Không tìm thấy từ: {user_text}"

    return jsonify({"text": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


