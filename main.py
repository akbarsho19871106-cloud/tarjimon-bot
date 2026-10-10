import asyncio, os, requests
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
    try:
        # 1. MyMemory - email билан 1000 та/кун
        r = requests.get(f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|{target}&de=youremail@gmail.com", timeout=10).json()
        if r.get('responseData', {}).get('translatedText'):
            return r['responseData']['translatedText']
    except: pass
    try:
        # 2. Lingva Translate - лимитсиз
        r = requests.get(f"https://lingva.ml/api/v1/auto/{target}/{text}", timeout=10).json()
        if r.get('translation'):
            return r['translation']
    except: pass
    return text

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("Salom! Men tarjimonman. 👋\n/ru Salom - ruschaga\n/tg Salom - tojikchaga\n/en Salom - inglizchaga\n/uz Salom - uzbekchaga")

@dp.message()
async def translate_handler(message: Message):
    txt = message.text
    if not txt: return
    if txt.startswith("/start"): return
    target = "ru"
    original = txt
    if txt.startswith("/") and " " in txt:
        parts = txt.split(" ", 1)
        target = parts[0][1:].split("@")[0][:2]
        original = parts[1]

    tr = translate_free(original, target)
    await message.answer(f"✅ ({target}):\n{tr}")

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
