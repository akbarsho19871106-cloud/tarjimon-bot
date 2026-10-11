import os, json, requests, urllib.parse, threading, asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 6641231347
FREE_LIMIT = 3
DB_FILE = "users.json"
LANGS = {"uz": "🇺🇿 Ўзбек", "tg": "🇹🇯 Тоҷикӣ", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

def load_db():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

def save_db(d):
    with open(DB_FILE, "w") as f: json.dump(d, f)

users = load_db()

def tr(text, dest):
    try:
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={q}"
        r = requests.get(url, timeout=10).json()
        return "".join([i[0] for i in r[0]])
    except:
        return text

app = Flask(__name__)
@app.route("/")
def home(): return "OK - Bot is Live"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- Handlers ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        users[uid] = {"count": 0, "paid": 0}
        save_db(users)
    if str(uid) == str(ADMIN_ID):
        await update.message.reply_text(f"Админ салом! ID: {ADMIN_ID}\n/vid ID ни бошқариш")
        return
    if users[uid]["count"] >= FREE_LIMIT and users[uid]["paid"] == 0:
        kb = [[InlineKeyboardButton("10 сўм - 50та", callback_data="buy_10")],[InlineKeyboardButton("Тўлов қилдим", callback_data="check")]]
        await update.message.reply_text("❌ Лимит тугади! Тўлов қилинг", reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = []
    row = []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    await update.message.reply_text("Тилни танланг:", reply_markup=InlineKeyboardMarkup(kb))

async def lang_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    dest = q.data.replace("lang_", "")
    context.user_data["lang"] = dest
    await q.edit_message_text(f"Тил танланди: {dest}. Энди матн юборинг!")

async def do_tr(update: Update, text: str):
    dest = update.effective_user.id
    # This function is internal
    pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users: users[uid] = {"count": 0, "paid": 0}
    lang = context.user_data.get("lang")
    if not lang:
        await start_handler(update, context)
        return
    # check limit
    if users[uid]["count"] >= FREE_LIMIT and users[uid]["paid"] == 0 and str(uid)!= str(ADMIN_ID):
        kb = [[InlineKeyboardButton("10 сўм - 50та", callback_data="buy_10")]]
        await update.message.reply_text("❌ Лимит тугади! Тўлов қилинг", reply_markup=InlineKeyboardMarkup(kb))
        return
    if str(uid)!= str(ADMIN_ID) and users[uid]["paid"] == 0:
        users[uid]["count"] += 1
        save_db(users)
    try:
        q = urllib.parse.quote(text[:1000])
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={lang}&dt=t&q={q}"
        r = requests.get(url, timeout=10).json()
        translated = "".join([i[0] for i in r[0]])
        src = r[2] if len(r) > 2 else "auto"
        await update.message.reply_text(f"{translated}\n\n_({src} -> {lang})_", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Таржима хато: {e}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cap = update.message.caption or ""
    if cap: await text_handler(update, context)
    else: await update.message.reply_text("Расм остига матн ёзинг!")

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("Тўлов учун: +992 92 123 45 67 (DC) га 10 сомони ташланг ва 'Тўлов қилдим' ни босинг")

async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("Админ текширади, 10 дақиқада очиб беради!")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    # Fix event loop error
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except: pass
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(lang_handler, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(buy_handler, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(check_handler, pattern="^check"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
