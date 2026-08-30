import telebot
from telebot import types

TOKEN = '8305229278:AAFeTrRPPhuwusUdUITTUuc75eJhTkdkPOI'
bot = telebot.TeleBot(TOKEN)

CHANNEL = '@SizningKanalUserNomi'  # Kanal username'ingizni shu yerga yozing

# 1, 2, 3, 4, 5 shaklidagi anime bazasi
ANIMALS_DB = {
    "1": {
        "file_id": "BURGA_YERGA_1-CHILIK_VIDEO_ID", 
        "caption": "🎬 **Nomi:** Anime 1-qism\n🎥 **Qism:** 1"
    },
    "2": {
        "file_id": "BURGA_YERGA_2-CHILIK_VIDEO_ID", 
        "caption": "🎬 **Nomi:** Anime 2-qism\n🎥 **Qism:** 2"
    },
    "3": {
        "file_id": "BURGA_YERGA_3-CHILIK_VIDEO_ID", 
        "caption": "🎬 **Nomi:** Anime 3-qism\n🎥 **Qism:** 3"
    },
    "4": {
        "file_id": "BURGA_YERGA_4-CHILIK_VIDEO_ID", 
        "caption": "🎬 **Nomi:** Anime 4-qism\n🎥 **Qism:** 4"
    },
    "5": {
        "file_id": "BURGA_YERGA_5-CHILIK_VIDEO_ID", 
        "caption": "🎬 **Nomi:** Anime 5-qism\n🎥 **Qism:** 5"
    }
}

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
        return False
    except:
        return False

def send_channels_markup():
    markup = types.InlineKeyboardMarkup()
    btn_channel = types.InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL.replace('@', '')}")
    btn_check = types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    markup.add(btn_channel)
    markup.add(btn_check)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    parts = text.split()
    anime_code = parts[1] if len(parts) > 1 else None

    if not check_subscription(user_id):
        bot.send_message(
            message.chat.id, 
            "⚠️ Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'ling:", 
            reply_markup=send_channels_markup()
        )
        return

    if anime_code and anime_code in ANIMALS_DB:
        item = ANIMALS_DB[anime_code]
        bot.send_video(message.chat.id, item["file_id"], caption=item["caption"], parse_mode="Markdown")
    else:
        bot.send_message(
            message.chat.id, 
            "Salom! 1, 2, 3, 4, 5 kabi raqamlardan birini yuboring yoki kanaldagi tugmani bosing! 🎬"
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_query(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "Rahmat, obuna tasdiqlandi! ✅")
        bot.send_message(call.message.chat.id, "Tabriklayman! Endi xohlagan raqamingizni yuborishingiz mumkin:")
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, "⚠️ Iltimos, avval kanalimizga obuna bo'ling!", reply_markup=send_channels_markup())
        return

    text = message.text.strip()
    if text in ANIMALS_DB:
        item = ANIMALS_DB[text]
        bot.send_video(message.chat.id, item["file_id"], caption=item["caption"], parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Bunday raqamdagi anime topilmadi. 1 dan 5 gacha raqam yuboring.")

bot.infinity_polling()
