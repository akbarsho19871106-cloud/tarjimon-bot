import asyncio, os, requests, urllib.parse
from flask import Flask
import threading
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6641231847 # Ўз ID нгизни ёзинг!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

def tr(text, to):
    try:
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to}&dt=t&q={q}"
        data = requests.get(url, timeout=10).json()
        return "".join([i[0] for i in data[0]])
    except:
        return text

@app.route('/')
def home(): return "OK"

@dp.message(Command("start"))
async def start_handler(m: Message):
    if m.from_user.id == ADMIN_ID:
        await m.answer("Салом Хўжайин! 👋\nРасм ҳам ишлайди энди!")
    else:
        await m.answer("Салом! Хабарингиз админга юборилди.")
        await bot.send_message(ADMIN_ID, f"📩 Янги мижоз:\n👤 {m.from_user.full_name}\n🆔 {m.from_user.id}\n\n📝 {m.text or m.caption or 'Расм юборди'}")
        if m.photo:
            await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=m.caption)

@dp.message()
async def all_handler(m: Message):
    # Агар расм бўлса
    if m.photo:
        if m.from_user.id!= ADMIN_ID:
            await bot.send_message(ADMIN_ID, f"📩 Расм келди:\n👤 {m.from_user.full_name}\n🆔 {m.from_user.id}")
            await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=m.caption or "")
            await m.answer("✅ Расмингиз админга юборилди!")
        else:
            # Сиз расм юборсангиз
            if m.reply_to_message:
                try:
                    client_id = int(m.reply_to_message.text.split("🆔")[1].split("\n")[0].strip())
                    await bot.send_photo(client_id, m.photo[-1].file_id, caption=m.caption or "")
                    await m.answer("✅ Расм юборилди!")
                except Exception as e:
                    await m.answer(f"❌ Reply қилиб юборинг! Хатолик: {e}")
        return

    # Текст бўлса
    text = m.text or m.caption or ""
    if not text:
        return

    if m.from_user.id == ADMIN_ID:
        if m.reply_to_message:
            try:
                client_id = int(m.reply_to_message.text.split("🆔")[1].split("\n")[0].strip())
                translated = f"📝 {text}\n\n🇷🇺 {tr(text,'ru')}\n🇹🇯 {tr(text,'tg')}\n🇺🇿 {tr(text,'uz')}\n🇺🇸 {tr(text,'en')}\n🇹🇷 {tr(text,'tr')}"
                await bot.send_message(client_id, translated)
                await m.answer("✅ Юборилди!")
            except:
                await m.answer("❌ Мижоз хабарига Reply қилиб ёзинг!")
        else:
            await m.answer(f"📝 {text}\n\n🇷🇺 {tr(text,'ru')}\n🇹🇯 {tr(text,'tg')}\n🇺🇿 {tr(text,'uz')}\n🇺🇸 {tr(text,'en')}\n🇹🇷 {tr(text,'tr')}")
    else:
        await bot.send_message(ADMIN_ID, f"📩 Янги мижоз:\n👤 {m.from_user.full_name} (@{m.from_user.username})\n🆔 {m.from_user.id}\n\n📝 Хабар: {text}")
        await m.answer("✅ Хабарингиз қабул қилинди!")

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
