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
def home(): return "OK"

def tr(text, to):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to}&dt=t&q={urllib.parse.quote(text)}"
        j = requests.get(url, timeout=10).json()
        return "".join([x[0] for x in j[0]])
    except:
        return text

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("5 til: /ru /tg /uz /en /tr\nMisol: /ru Salom")

@dp.message()
async def h(msg: Message):
    t = msg.text
    if not t: return
    lang = "ru"
    txt = t
    if t.startswith("/") and " " in t:
        p = t.split(" ", 1)
        lang = p[0][1:].lower()[:2]
        txt = p[1]
    res = tr(txt, lang)
    await msg.answer(f"({lang}): {res}")

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
