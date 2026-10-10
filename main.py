import asyncio, os
from flask import Flask
import threading
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from deep_translator import MyMemoryTranslator, LibreTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

@app.route('/')
def home(): return "Bot ishlayapti!"

def safe_translate(text, target):
    try:
        return MyMemoryTranslator(source='auto', target=target).translate(text)
    except:
        try:
            return LibreTranslator(source='auto', target=target).translate(text)
        except:
            return f"{text} [{target}]"

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("Salom! 👋 /ru /tg /en /uz")

@dp.message()
async def translate_handler(message: Message):
    txt = message.text
    if not txt: return
    if txt.startswith("/start"): return
    parts = txt.split(" ", 1)
    if len(parts)>1 and parts[0].startswith("/"):
        tgt = parts[0][1:3]
        org = parts[1]
    else:
        tgt = "ru"
        org = txt
    tr = safe_translate(org, tgt)
    await message.answer(f"✅ ({tgt}):\n{tr}")

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
