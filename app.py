from flask import Flask, request, jsonify
import json
import re
import os

app = Flask(__name__)

# ================== HOME ==================
@app.route("/", methods=["GET"])
def home():
    return "SERVER OK"


# ================== LOAD DATA ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
fpath = os.path.join(BASE_DIR, "medictdata_o.json")

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s’']", "", text)  # giữ dấu '
    return re.sub(r"\s+", " ", text).strip()

with open(fpath, "r", encoding="utf-8") as f:
    raw_dict = json.load(f)

# chuẩn hoá toàn bộ key trong từ điển
dictionary = {}
for k, v in raw_dict.items():
    dictionary[normalize(k)] = v

print("TOTAL WORDS:", len(dictionary))
print("SAMPLE KEYS:", list(dictionary.keys())[:10])


# ================== WEBHOOK ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("DATA FROM ZALO:", data)

    # Zalo có nhiều event hệ thống
    if not data or "message" not in data:
        return jsonify({"text": "ℹ️ Event hệ thống, chưa có tin nhắn"})

    message = data.get("message", {})
    user_text = message.get("text")

    if not user_text:
        return jsonify({"text": "❌ Tin nhắn không phải dạng text"})

    key = normalize(user_text)
    item = None
    found_key = None

    # 1️⃣ match chính xác
    if key in dictionary:
        item = dictionary[key]
        found_key = key
    else:
        # 2️⃣ match gần đúng (bearing -> ball bearing)
        for k in dictionary:
            if key in k:
                item = dictionary[k]
                found_key = k
                break

    if item:
        reply = (
            f"🔤 {found_key}\n"
            f"{item.get('ipa', '')}\n\n"
            f"🇻🇳 {item.get('meaning_vi', '')}\n\n"
            f"📘 {item.get('example_en', '')}\n"
            f"📙 {item.get('example_vi', '')}\n"
            f"📚 {item.get('book', '')} – Lesson {item.get('lesson', '')}"
        )
    else:
        reply = f"❌ Không tìm thấy thuật ngữ: {user_text}"

    return jsonify({"text": reply})


# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
