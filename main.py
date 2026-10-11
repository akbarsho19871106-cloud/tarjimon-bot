import telebot
import os
from deep_translator import MyMemoryTranslator
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_lang = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇺🇿 Ўзбек", callback_data="uz"),
        telebot.types.InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="tg"),
        telebot.types.InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
        telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data="en")
    )
    bot.send_message(message.chat.id, "Тилни танланг / Забонро интихоб кунед:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def lang(call):
    user_lang[call.message.chat.id] = call.data
    langs = {"uz":"Ўзбек","tg":"Тоҷикӣ","ru":"Русский","en":"English"}
    bot.send_message(call.message.chat.id, f"Тил танланди: {langs.get(call.data)} ✅ Энди матн юборинг!")

@bot.message_handler(func=lambda m: True)
def trans(message):
    try:
        dest = user_lang.get(message.chat.id, 'ru')
        # MyMemory - чекловсиз
        result = MyMemoryTranslator(source='auto', target=dest).translate(message.text)
        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато, қайта ёзинг: {e}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
