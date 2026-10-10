
import asyncio, os, requests, urllib.parse, json
from flask import Flask
import threading
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6641231847

FREE_LIMIT = 3

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

    # Админ учун алоҳида
    if m.from_user.id == ADMIN_ID:
        await m.answer(f"Салом Хўжайин! 👑\nID: {ADMIN_ID}\nБот ишлаяпти! ✅\n3 та бепул система ёқилган!")
        return

    left = FREE_LIMIT - users[uid]["count"]
    if users[uid]["paid"] > 0:
        await m.answer(f"Салом! 💎 Сизда {users[uid]['paid']} та бор!\nМатн ёки расм юборинг!")
    elif left > 0:
        await m.answer(f"Салом! 👋 Сизда {left} та БЕПУЛ қолди!\nМатн ёки расм юборинг!")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 10 сомони - 50 та", callback_data="buy10")],
            [InlineKeyboardButton(text="💎 20 сомони - Чексиз", callback_data="buy20")]
        ])
        await m.answer(f"❌ Бепул тугади!\nПуллик олинг:", reply_markup=kb)

@dp.message(Command("reset"))
async def reset_handler(m: Message):
    if m.from_user.id!= ADMIN_ID: return
    users.clear()
    save_db(users)
    await m.answer("✅ База тозаланди! Энди ҳаммада яна 3 та бепул бор!")

@dp.message(Command("add"))
async def add_handler(m: Message):
    if m.from_user.id!= ADMIN_ID: return
    try:
        _, uid, amount = m.text.split()
        if uid not in users: users[uid] = {"count": 3, "paid": 0}
        users[uid]["paid"] += int(amount)
        save_db(users)
        await m.answer(f"✅ {uid} га {amount} та қўшилди!")
        await bot.send_message(int(uid), f"✅ Сизга {amount} та қўшилди! Ёзишингиз мумкин!")
    except:
        await m.answer("Формат: /add ID СОН")

@dp.callback_query(F.data.startswith("buy"))
async def buy_handler(c: CallbackQuery):
    await c.message.answer(f"💰 Тўлаш учун админга ёзинг: @{ADMIN_ID} - ёки шу ботда қолдиринг!")
    await bot.send_message(ADMIN_ID, f"💰 МИЖОЗ ПУЛ ТЎЛАМОҚЧИ!\n👤 {c.from_user.full_name}\n🆔 {c.from_user.id}\nТариф: {c.data}")

# АСОСИЙ ҚИСМ - РАСМ ВА ТЕКСТ
@dp.message(F.photo)
async def photo_handler(m: Message):
    uid = str(m.from_user.id)
    if uid not in users: users[uid] = {"count": 0, "paid": 0}

    caption = m.caption or "Расм"

    # АДМИН бўлса - чексиз
    if m.from_user.id == ADMIN_ID:
        await m.answer(f"📸 Расм қабул қилинди Хўжайин!\n📝 {caption}\n\n🇷🇺 {tr(caption,'ru')}\n🇹🇯 {tr(caption,'tg')}\n🇺🇿 {tr(caption,'uz')}")
        return

    # КЛИЕНТ - расмни админга юбориш
    await bot.send_message(ADMIN_ID, f"📩 РАСМ КЕЛДИ!\n👤 {m.from_user.full_name}\n🆔 {m.from_user.id}\n📝 {caption}")
    await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption)

    # Пул текшириш
    if users[uid]["paid"] > 0:
        users[uid]["paid"] -= 1
        save_db(users)
        await m.answer(f"✅ Расмингиз админга юборилди!\n💎 {users[uid]['paid']} та қолди\n📝 {caption}")
    elif users[uid]["count"] < FREE_LIMIT:
        users[uid]["count"] += 1
        left = FREE_LIMIT - users[uid]["count"]
        save_db(users)
        await m.answer(f"✅ Расмингиз қабул қилинди!\n🆓 {left} та бепул қолди\n📝 {caption}\n🇷🇺 {tr(caption,'ru')}\n🇹🇯 {tr(caption,'tg')}")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 10 сомони - 50 та", callback_data="buy10")]
        ])
        await m.answer(f"❌ Бепул тугади! Расм юбориш ҳам пуллик!", reply_markup=kb)

@dp.message(F.text)
async def text_handler(m: Message):
    if m.text.startswith("/"): return
    uid = str(m.from_user.id)
    if uid not in users: users[uid] = {"count": 0, "paid": 0}

    if m.from_user.id == ADMIN_ID:
        txt = m.text
        await m.answer(f"📝 {txt}\n\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
        return

    txt = m.text
    await bot.send_message(ADMIN_ID, f"📩 Хабар:\n👤 {m.from_user.full_name}\n🆔 {m.from_user.id}\n📝 {txt}")

    if users[uid]["paid"] > 0:
        users[uid]["paid"] -= 1
        save_db(users)
        await m.answer(f"💎 ({users[uid]['paid']} қолди)\n📝 {txt}\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
    elif users[uid]["count"] < FREE_LIMIT:
        users[uid]["count"] += 1
        left = FREE_LIMIT - users[uid]["count"]
        save_db(users)
        await m.answer(f"🆓 ({left} қолди)\n📝 {txt}\n🇷🇺 {tr(txt,'ru')}\n🇹🇯 {tr(txt,'tg')}\n🇺🇿 {tr(txt,'uz')}\n🇺🇸 {tr(txt,'en')}\n🇹🇷 {tr(txt,'tr')}")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 10 сомони - 50 та", callback_data="buy10")],
            [InlineKeyboardButton(text="💎 20 сомони - Чексиз", callback_data="buy20")]
        ])
        await m.answer(f"❌ Бепул 3 та тугади!", reply_markup=kb)

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
