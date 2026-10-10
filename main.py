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
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to}&dt=t&q={q}"
        data = requests.get(url, timeout=10).json()
        return "".join([i[0] for i in data[0]])
    except:
        return text

@dp.message(Command("start"))
async def start_handler(m: Message):
    await m.answer("Салом деб ёзинг, 5 тилда чиқараман! 👇\n/ru /en /tg /uz /tr дан бирига алоҳида ҳам қилади")

@dp.message()
async def h(msg: Message):
    t = msg.text or ""
    if not t: return

    # Agar /ru Salom deb yozsa - faqat bitta tilga
    if t.startswith("/") and " " in t:
        a,b = t.split(" ",1)
        c = a[1:].lower()[:2]
        if c in ["ru","tg","uz","en","tr"]:
            res = tr(b, c)
            await msg.answer(f"({c}): {res}")
            return

    # Oddiy "Salom" deb yozsa - 5 tasi birda
    ru = tr(t, "ru")
    tg = tr(t, "tg")
    uz = tr(t, "uz")
    en = tr(t, "en")
    tr_tr = tr(t, "tr")

    javob = f"📝 {t}\n\n🇷🇺 ru: {ru}\n🇹🇯 tg: {tg}\n🇺🇿 uz: {uz}\n🇺🇸 en: {en}\n🇹🇷 tr: {tr_tr}"
    await msg.answer(javob)

async def start_bot():
    await dp.start_polling(bot)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_bot())
