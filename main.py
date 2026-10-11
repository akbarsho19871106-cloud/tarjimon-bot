import os, json, requests, urllib.parse, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=6641231847
FREE_LIMIT=3
DB_FILE="users.json"
LANGS={"uz":"🇺🇿 Ўзбек","tg":"🇹🇯 Тожикӣ","ru":"🇷🇺 Русский","en":"🇬🇧 English","tr":"🇹🇷 Türkçe"}
def load_db():
 try:
  with open(DB_FILE,"r") as f: return json.load(f)
 except: return {}
def save_db(d):
 with open(DB_FILE,"w") as f: json.dump(f,d)
users=load_db()
def tr(text,dest):
 try:
  q=urllib.parse.quote(text)
  url=f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={q}"
  r=requests.get(url,timeout=10).json()
  return "".join([i[0] for i in r[0]])
 except: return text
app=Flask(__name__)
@app.route("/")
def home(): return "OK"
def run_flask(): app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
async def start_handler(update,context):
 uid=str(update.effective_user.id)
 if uid not in users: users[uid]={"count":0,"paid":0};save_db(users)
 if str(uid)==str(ADMIN_ID):
  await update.message.reply_text(f"Админ салом! ID:{ADMIN_ID}\n/add ID miqdor\n/reset")
  return
 left=FREE_LIMIT-users[uid]["count"]
 if users[uid]["paid"]>0: left=users[uid]["paid"]
 if left>0: await update.message.reply_text(f"Салом! 5 тилда таржимонман 🇺🇿🇹🇯🇷🇺🇬🇧🇹🇷\nСизда {left} та лимит бор. Матн ёки расм юборинг!")
 else:
  kb=[[InlineKeyboardButton("10 сўров - 50т",callback_data="buy_10")],[InlineKeyboardButton("20 сўров - 90т",callback_data="buy_20")]]
  await update.message.reply_text("❌ Лимит тугади! Тўлов қилинг:",reply_markup=InlineKeyboardMarkup(kb))
async def check_limit(update):
 uid=str(update.effective_user.id)
 if uid not in users: users[uid]={"count":0,"paid":0}
 if str(uid)==str(ADMIN_ID): return True
 if users[uid]["paid"]>0: users[uid]["paid"]-=1;save_db(users);return True
 if users[uid]["count"]<FREE_LIMIT: users[uid]["count"]+=1;save_db(users);return True
 return False
async def do_tr(text,update):
 ok=await check_limit(update)
 if not ok:
  kb=[[InlineKeyboardButton("10 - 50т",callback_data="buy_10")],[InlineKeyboardButton("20 - 90т",callback_data="buy_20")]]
  await update.message.reply_text("❌ Лимит тугади",reply_markup=InlineKeyboardMarkup(kb));return
 try:
  q=urllib.parse.quote(text[:100])
  r=requests.get(f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={q}",timeout=5).json()
  src=r[2] if len(r)>2 else "auto"
 except: src="auto"
 res=f"📝 Оригинал ({src}):\n{text}\n\n"
 for code,name in LANGS.items():
  if code==src: continue
  res+=f"{name}:\n{tr(text,code)}\n\n"
 await update.message.reply_text(res)
async def text_handler(update,context): await do_tr(update.message.text,update)
async def photo_handler(update,context):
 cap=update.message.caption or ""
 if cap: await do_tr(cap,update)
 else:
  ok=await check_limit(update)
  if not ok: await update.message.reply_text("❌ Лимит тугади");return
  await update.message.reply_text("📸 Расм қабул қилинди! Матн ёзиб юборинг, 5 тилга таржима қиламан!")
async def buy_handler(update,context):
 q=update.callback_query;await q.answer()
 await q.message.reply_text(f"Тўлов учун: @akbarsho\nID:{q.from_user.id}\n{q.data}")
async def add_handler(update,context):
 if str(update.effective_user.id)!=str(ADMIN_ID): return
 try:
  _,uid,amt=update.message.text.split();amt=int(amt)
  if uid not in users: users[uid]={"count":0,"paid":0}
  users[uid]["paid"]+=amt;save_db(users)
  await update.message.reply_text(f"✅ {uid} га {amt} қўшилди!")
  try: await context.bot.send_message(int(uid),f"✅ Сизга {amt} та лимит берилди!")
  except: pass
 except: await update.message.reply_text("/add ID MIQDOR")
async def reset_handler(update,context):
 if str(update.effective_user.id)!=str(ADMIN_ID): return
 global users;users={};save_db(users);await update.message.reply_text("Тозаланди!")
def main():
 threading.Thread(target=run_flask,daemon=True).start()
 if not BOT_TOKEN: return
 b=ApplicationBuilder().token(BOT_TOKEN).build()
 b.add_handler(CommandHandler("start",start_handler))
 b.add_handler(CommandHandler("add",add_handler))
 b.add_handler(CommandHandler("reset",reset_handler))
 b.add_handler(CallbackQueryHandler(buy_handler))
 b.add_handler(MessageHandler(filters.PHOTO,photo_handler))
 b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))
 b.run_polling()
if __name__=="__main__": main()
