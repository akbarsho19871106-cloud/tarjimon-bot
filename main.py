import asyncio, logging, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from deep_translator import GoogleTranslator

TOKEN=os.getenv("BOT_TOKEN")

def translate_text(text,target='tg'):
    try: return GoogleTranslator(source='auto',target=target).translate(text)
    except Exception as e: return f"Хато: {e}"

bot=Bot(token=TOKEN)
dp=Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Салом! 👋 Мен таржимонман.\n/ru Салом - русчага\n/tg Салом - точикчага\n/en Салом - инглизчага")

@dp.message()
async def handle(message: types.Message):
    text=message.text or ""
    if not text: return
    target='tg'; clean=text
    if text.startswith('/tg '): target='tg'; clean=text[4:]
    elif text.startswith('/ru '): target='ru'; clean=text[4:]
    elif text.startswith('/en '): target='en'; clean=text[4:]
    elif text.startswith('/'): clean=text.split(' ',1)[-1]
    result=translate_text(clean,target)
    await message.answer(f"✅ ({target}):\n{result}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
