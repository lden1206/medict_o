from flask import Flask, request
from zalo_bot import Bot, Update
from zalo_bot.ext import Dispatcher, MessageHandler, filters
import json
import os
import re

# ====== LOAD DICTIONARY ======
with open("medictdata_o.json", "r", encoding="utf-8") as f:
    DICT = json.load(f)

def normalize(text):
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)

# ====== INIT BOT ======
TOKEN = os.getenv("ZALO_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# ====== MESSAGE HANDLER ======
def handle_message(update, context):
    user_text = update.message.text
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
            f"{item.get('ipa','')}\n\n"
            f"🇻🇳 {item.get('meaning_vi','')}\n\n"
            f"📘 {item.get('example_en','')}\n"
            f"📙 {item.get('example_vi','')}\n"
            f"📚 {item.get('book','')} – Lesson {item.get('lesson','')}"
        )
    else:
        reply = f"❌ Không tìm thấy từ: {user_text}"

    update.message.reply_text(reply)

dispatcher.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

# ====== WEBHOOK ======
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def home():
    return "Zalo Dictionary Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
