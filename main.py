
import asyncio, os, requests, urllib.parse, json
from flask import Flask
import threading
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6641231847 # Ўз ID нгиз @userinfobot

FREE_LIMIT = 3
PRICE_10 = "10 сомони - 50 та"
PRICE_20 = "20 сомони - Чексиз 1 ой"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

DB_FILE = "users.json"
def load_db():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(f, data)

users = load_db()

def tr(text, to):
    try:
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={to}&dt=t&q={q}"
        r = requests.get(url, timeout=10).json()
        return "".join([i[0] for i in r[0]])
    except: return text

@app.route('/')
def home(): return "OK"

@dp.message(Command("start"))
async def start_handler(m: Message):
    uid = str(m.from_user.id)
    if uid not in users:
        users[uid] = {"count": 0, "paid": 0}
        save_db(users)
    left = FREE_LIMIT - users[uid]["count"]
    if users[uid]["paid"] > 0:
        await m.answer(f"Салом! 💎 Сизда {users[uid]['paid']} та пуллик бор!\nМатн ёзинг!")
    elif left > 0:
        await m.answer(f"Салом! 👋 Сизда {left} та БЕПУЛ қолди!\n3 тадан кейин пуллик.\nМатн ёзинг!")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 {PRICE_10}", callback_data="buy10")],
            [InlineKeyboardButton(text=f"💎 {PRICE_20}", callback_data="buy20")]
        ])
        await m.answer(f"❌ Бепул 3 та тугади!\nПуллик олинг:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy"))
async def buy_handler(c: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Тўлаш - Админ", url=f"tg://user?id={ADMIN_ID}")]
    ])
    await c.message.answer(f"💰 Тўлов учун админга ёзинг!\nТўловдан кейин очиб берамиз!", reply_markup=kb)
    await bot.send_message(ADMIN_ID, f"💰 ПУЛЛИК МИЖОЗ!\n👤 {c.from_user.full_name}\n🆔 {c.from_user.id}\nТариф: {c.data}")

@dp.message(Command("add"))
async def add_handler(m: Message):
    if m.from_user.id!= ADMIN_ID: return
    try:
        _, uid, amount = m.text.split()
        if uid not in users: users[uid] = {"count": 3, "paid": 0}
        users[uid]["paid"] += int(amount)
        save_db(users)
        await m.answer(f"✅ {uid} га {amount} та қўшилди!")
        await bot.send_message(int(uid), f"✅ Сизга {amount} та таржима қўшилди!")
    except:
        await m.answer("Формат: /add ID СОН\nМисол: /add 123456789 50")

@dp.message()
async def all_handler(m: Message):
    uid = str(m.from_user.id)
    if uid not in users: users[uid] = {"count": 0, "paid": 0}

    # Админ чексиз
    if m.from_user.id == ADMIN_ID and m.text and not m.text.startswith("/"):
        txt = m.text or m.caption or ""
        await m.answer(f"📝 {txt}\n\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
        return

    txt = m.text or m.caption or ""
    if not txt:
        if m.photo:
            await m.answer("📸 Расм келди! Устига текст ёзиб юборинг!")
        return

    if users[uid]["paid"] > 0:
        users[uid]["paid"] -= 1
        save_db(users)
        await m.answer(f"💎 Пуллик ({users[uid]['paid']} қолди)\n\n📝 {txt}\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
    elif users[uid]["count"] < FREE_LIMIT:
        users[uid]["count"] += 1
        save_db(users)
        left = FREE_LIMIT - users[uid]["count"]
        await m.answer(f"🆓 Бепул ({left} қолди)\n\n📝 {txt}\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 {PRICE_10}", callback_data="buy10")],
            [InlineKeyboardButton(text=f"💎 {PRICE_20}", callback_data="buy20")]
        ])
        await m.answer(f"❌ Бепул тугади! Пуллик олинг:", reply_markup=kb)
        await bot.send_message(ADMIN_ID, f"⚠️ Лимит тугади:\n👤 {m.from_user.full_name}\n🆔 {m.from_user.id}")

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
