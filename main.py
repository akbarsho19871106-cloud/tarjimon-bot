
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from deep_translator import GoogleTranslator
import time

TOKEN = os.getenv("BOT_TOKEN")

def translate_text(text, dest='tg'):
    try:
        time.sleep(0.8)
        return GoogleTranslator(source='auto', target=dest).translate(text)
    except Exception as e:
        return f"Хато: {e}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Салом! 👋 Мен таржимонман.\n/ru Салом - русчага\n/tg Салом - тоҷикчага\n/en Салом - инглизчага\n/uz Салом - ўзбекчага\n\nМатн ёзинг!")

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
    else:
        parts = clean.rsplit(' ', 1)
        if len(parts)==2 and parts[-1] in ['tg','ru','en','uz']:
            clean, dest = parts[0], parts[-1]

    result = translate_text(clean, dest)
    await message.answer(f"✅ ({dest}):\n{result}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
