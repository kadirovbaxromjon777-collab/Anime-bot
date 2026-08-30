from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# SIZNING BOTINGIZ VA KANALINGIZ UCHUN TAYYOR KOD
app = Client(
    "my_anime_bot",
    api_id=29384756,  # O'zingizning API ID raqamingizni yozasiz
    api_hash="1234567890abcdef1234567890abcdef",  # API Hash
    bot_token="8305229278:AAFeTrRPPuwusUdUITTUuc75eJhTkdkPOI"  # Botingiz tokeni
)

CHANNEL_USERNAME = "@Anidone_uz_animelar"  # Kanalingiz

@app.on_message(filters.command("post"))
def send_anime_post(client, message):
    # Yuklab olish tugmasi
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📥 Yuklab olish", 
                    url="https://t.me/Anidone_uz_animelar?start=1"
                )
            ]
        ]
    )
    
    # Anime haqida matn
    caption_text = (
        "🎬 Nomi: Vaqt Nigohidan tashqarida\n"
        "📑 Qism: 4\n"
        "🎙 Ovoz berdi: Shakh va Meduca"
    )
    
    # Kanalga rasm va matnni yuborish
    client.send_photo(
        chat_id=CHANNEL_USERNAME,
        photo="https://telegra.ph/file/example.jpg",  # Shu yerga rasmingiz havolasini qo'yasiz
        caption=caption_text,
        reply_markup=keyboard
    )
    message.reply("Post kanalga muvaffaqiyatli tashlandi!")

app.run()
