import telebot, os, threading
from flask import Flask
import translators as ts

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Live!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом Акбар! Матн ёзинг, мен 4 тилга таржима қиламан:\n🇺🇿 Ўзбек\n🇹🇯 Тоҷикӣ\n🇷🇺 Русский\n🇬🇧 English")

@bot.message_handler(func=lambda m: True)
def translate(message):
    if message.text.startswith('/'): return
    try:
        txt = message.text
        uz = ts.translate_text(txt, to_language='uz', translator='google')
        tg = ts.translate_text(txt, to_language='tg', translator='google')
        ru = ts.translate_text(txt, to_language='ru', translator='google')
        en = ts.translate_text(txt, to_language='en', translator='google')
        
        res = f"🇺🇿 Ўзбек: {uz}\n\n🇹🇯 Тоҷикӣ: {tg}\n\n🇷🇺 Русский: {ru}\n\n🇬🇧 English: {en}"
        bot.send_message(message.chat.id, res)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато: {e}")

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_web).start()
bot.infinity_polling()
