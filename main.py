from flask import Flask
import threading
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from deep_translator import GoogleTranslator
import time

app = Flask(__name__)
@app.route('/')
def home(): return "Bot ishlayapti!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()

TOKEN = os.getenv("BOT_TOKEN")

def translate_text(text, dest='tg'):
    try:
        time.sleep(0.8)
        return GoogleTranslator(source='auto', target=dest).translate(text)
    except Exception as e:
        return f"Xato: {e}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Salom! Men tarjimonman.\n/ru Salom - ruschaga\n/tg Salom - tojikchaga\n/en Salom - inglizchaga\n/uz Salom - uzbekchaga")

@dp.message()
async def handle(message: types.Message):
    text = message.text or ""
    if not text:
        return
    dest = 'tg'
    clean = text
    if text.startswith('/tg '):
        dest='tg'; clean=text[4:]
    elif text.startswith('/ru '):
        dest='ru'; clean=text[4:]
    elif text.startswith('/en '):
        dest='en'; clean=text[4:]
    elif text.startswith('/uz '):
        dest='uz'; clean=text[4:]
    result = translate_text(clean, dest)
    await message.answer(f"{dest}: {result}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
