import telebot, os, threading
from flask import Flask
import translators as ts

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_lang = {}

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Live!"

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇺🇿 Узбек", callback_data="uz"),
        telebot.types.InlineKeyboardButton("🇹🇯 Тожик", callback_data="tg"),
        telebot.types.InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
        telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data="en")
    )
    bot.send_message(message.chat.id, "Тилни танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def set_lang(call):
    user_lang[call.message.chat.id] = call.data
    bot.send_message(call.message.chat.id, f"✅ {call.data} танланди. Энди матн ёзинг!")

@bot.message_handler(func=lambda m: True)
def translate(message):
    if message.text.startswith('/'):
        return
    dest = user_lang.get(message.chat.id, 'ru')
    try:
        translated = ts.translate_text(message.text, to_language=dest, translator='google')
        bot.send_message(message.chat.id, translated)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато: {e}")

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_web).start()
bot.infinity_polling()
