import asyncio
import os
from flask import Flask
import threading
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from deep_translator import MyMemoryTranslator, GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def safe_translate(text, target):
    # 1-ўринда MyMemory - бепул, чеклов йўқ
    try:
        return MyMemoryTranslator(source='auto', target=target).translate(text)
    except:
        pass
    # 2-ўринда Google - запас
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except Exception as e:
        return f"Ҳозир банд, 1 дақиқадан кейин қайта уриниб кўринг. ({target})"

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Salom! 👋 Men tarjimonman.\n/ru Salom - ruschaga\n/tg Salom - tojikchaga\n/en Salom - inglizchaga\n/uz Salom - uzbekchaga")

@dp.message()
async def translate_handler(message: Message):
    text = message.text
    if not text: return
    target = "ru"
    original = text
    if text.startswith("/ru "):
        target = "ru"
        original = text[4:]
    elif text.startswith("/tg "):
        target = "tg"
        original = text[4:]
    elif text.startswith("/en "):
        target = "en"
        original = text[4:]
    elif text.startswith("/uz "):
        target = "uz"
        original = text[4:]
    elif text.startswith("/"):
        if text.startswith("/start"): return
        target = text[1:3]
        original = text[4:]
    translated = safe_translate(original, target)
    await message.answer(f"✅ ({target}):\n{translated}")

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
