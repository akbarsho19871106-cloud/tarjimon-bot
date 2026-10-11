import telebot
import os
from googletrans import Translator

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇺🇿 Ўзбек", callback_data="uz"),
        telebot.types.InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="tg"),
        telebot.types.InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
        telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data="en")
    )
    bot.send_message(message.chat.id, "Тилни танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def lang(call):
    user_lang[call.message.chat.id] = call.data
    bot.send_message(call.message.chat.id, f"Тил танланди: {call.data}. Энди матн юборинг!")

@bot.message_handler(func=lambda m: True)
def trans(message):
    try:
        dest = user_lang.get(message.chat.id, 'ru')
        txt = message.text
        res = translator.translate(txt, dest=dest)
        bot.send_message(message.chat.id, res.text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Хато: {e}")

bot.infinity_polling()
