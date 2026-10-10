
import asyncio, os, requests, urllib.parse
from flask import Flask
import threading
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

@app.route('/')
def home(): return "Bot ishlayapti!"

def translate_free(text, target='ru'):
    target = target.lower()[:2]
    if target not in ['ru','en','tg','uz']: target='ru'
    enc_text = urllib.parse.quote(text)
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target}&dt=t&q={enc_text}"
        r = requests.get(url, timeout=10).json()
        result = "".join([x[0] for x in r[0]])
        if result:
            return result
    except:
        pass
    return text

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("Salom! Tarjimon bot 👋\n/ru Salom - ruschaga\n/tg Salom - tojikchaga\n/en Salom - inglizchaga")

@dp.message()
async def translate_handler(message: Message):
    txt = message.text
    if not txt: return
    if txt == "/start": return
    target = "ru"
    original = txt
    if txt.startswith("/") and " " in txt:
        parts = txt.split(" ", 1)
        target = parts[0][1:].split("@")[0][:2]
        original = parts[1]
    tr = translate_free(original, target)
    await message.answer(f"✅ ({target}): {tr}")

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
