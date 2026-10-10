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

def tr(text, to):
    try:
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to}&dt=t&q={q}"
        r = requests.get(url, timeout=10).json()
        return "".join([i[0] for i in r[0]])
    except Exception as e:
        return text

@app.route('/')
def home(): return "OK"

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("Салом деб ёзинг, 5 тилда чиқараман! 👇\n/ru /en /tg /uz /tr")

@dp.message()
async def all_handler(m: Message):
    text = (m.text or m.caption or "").strip()
    if not text:
        return
    if text.startswith("/"):
        try:
            lang, txt = text.split(" ", 1)
            lang = lang[1:].lower()
            if lang in ["ru","tg","uz","en","tr"]:
                await m.answer(f"✅ ({lang}): {tr(txt, lang)}")
            else:
                await m.answer("Формат: /ru Салом")
        except:
            pass
        return

    # 5 тилда
    await m.answer(
        f"📝 {text}\n\n"
        f"🇷🇺 ru: {tr(text,'ru')}\n"
        f"🇹🇯 tg: {tr(text,'tg')}\n"
        f"🇺🇿 uz: {tr(text,'uz')}\n"
        f"🇺🇸 en: {tr(text,'en')}\n"
        f"🇹🇷 tr: {tr(text,'tr')}"
    )

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
