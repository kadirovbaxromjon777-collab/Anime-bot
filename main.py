import telebot
from telebot import types

TOKEN = '8305229278:AAFeTrRPPhuwusUdUITTUuc75eJhTkdkPOI'
bot = telebot.TeleBot(TOKEN)

CHANNEL = '@Anidone_uzbek_tilida'

# Anime kodlari va ma'lumotlari (kodlarni o'zingiz xohlagancha o'zgartirishingiz mumkin)
ANIMALS_DB = {
    "1": "🎬 **Nomi:** Vaqt Nigohidan tashqarida\n🎥 **Qism:** 4\n🎙 **Ovoz berdi:** Shakh va Meduca",
    "2": "🎬 **Nomi:** Naruto\n🎥 **Qism:** 1-220\n🎙 **Ovoz berdi:** Uzbek tilida",
    "3": "🎬 **Nomi:** One Piece\n🎥 **Qism:** Barcha qismlar\n🎙 **Ovoz berdi:** Studio",
    "4": "🎬 **Nomi:** Jujutsu Kaisen\n🎥 **Qism:** 24-qism\n🎙 **Ovoz berdi:** UzDub",
    "5": "🎬 **Nomi:** Demon Slayer\n🎥 **Qism:** 11-qism\n🎙 **Ovoz berdi:** Studio"
}

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
        return False
    except:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL.replace('@', '')}")
        btn_check = types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
        markup.add(btn_channel)
        markup.add(btn_check)
        
        bot.send_message(
            message.chat.id, 
            "⚠️ Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'ling:", 
            reply_markup=markup
        )
        return

    bot.send_message(
        message.chat.id, 
        "Salom! Anime kodini yuboring (masalan: **746**, **286**, **762**...), men sizga animeni topib beraman! 🎬"
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_query(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "Rahmat, obuna tasdiqlandi! ✅")
        bot.send_message(call.message.chat.id, "Endi anime kodini yuborishingiz mumkin:")
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

@bot.message_handler(func=lambda message: True)
def send_anime(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "⚠️ Iltimos, avval /start buyrug'ini bosing va kanalga obuna bo'ling!")
        return

    text = message.text.strip().lower()

    if text in ANIMALS_DB:
        bot.send_message(message.chat.id, ANIMALS_DB[text], parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Bunday koddagi anime topilmadi yoki noto'g'ri kod kiritdingiz.")

bot.infinity_polling()
