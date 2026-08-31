import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)
from pyrogram.errors import UserNotParticipant, ChatAdminRequired

# Pyrogram Bot sozlamalari
app = Client(
    "anidone_bot",
    api_id=36275728,
    api_hash="62384c5845916b8ac25996f83154a13b",
    bot_token="8305229278:AAHI7DsmLdwysKFf0N5IFmFz4yT2CRnGOzs",
)

CHANNEL_ID = -1003754381541
CHANNEL_LINK = "https://t.me"

# Anime bazasi (Yangi video va nomi shu yerga muvaffaqiyatli qo'shildi)
ANIMES = {
    "1": {
        "title": "Xazina izlovchi",
        "part": "8-qism",
        "video": "AAMCAgADGQEDhL1XapVM7-7qrdXRg9TgkscQ8dGHQJQAAlipAAJQTqBI98EUuHI1o2IBAAdtAAM9BA"
    },
    "746": {
        "title": "Vaqt Nigohidan tashqarida",
        "part": "4-qism",
        "video": "AAMCAgADGQEDhL1XapVM7-7qrdXRg9TgkscQ8dGHQJQAAlipAAJQTqBI98EUuHI1o2IBAAdtAAM9BA" # Namunaviy kod
    }
}


async def check_subscription(client, user_id):
  try:
    await client.get_chat_member(CHANNEL_ID, user_id)
    return True
  except UserNotParticipant:
    return False
  except (ChatAdminRequired, Exception):
    return True


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
  user_id = message.from_user.id
  if not await check_subscription(client, user_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")],
    ])
    await message.reply(
        "⚠️ Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'ling:",
        reply_markup=keyboard,
    )
  else:
    await message.reply(
        "Salom! Anime kodini yuboring (masalan: **1**, **746**...), men"
        " sizga animeni topib beraman! 🎬"
    )


@app.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client, callback: CallbackQuery):
  user_id = callback.from_user.id
  if await check_subscription(client, user_id):
    await callback.message.edit_text(
        "✅ Rahmat! Obuna tasdiqlandi. Endi anime kodini yuboring:"
    )
  else:
    await callback.answer(
        "❌ Siz hali kanalga obuna bo'lmagansiz!", show_alert=True
    )


@app.on_message(filters.text & ~filters.command(["start"]))
async def find_anime(client, message: Message):
  user_id = message.from_user.id

  if not await check_subscription(client, user_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")],
    ])
    await message.reply(
        "⚠️ Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'ling:",
        reply_markup=keyboard,
    )
    return

  code = message.text.strip()

  if code in ANIMES:
    anime = ANIMES[code]
    caption = f"🎬 Nomi: {anime['title']}\n📑 Qism: {anime['part']}"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Yuklab olish", url=CHANNEL_LINK)]]
    )

    # Rasm o'rniga to'g'ridan-to'g'ri video yuborish funksiyasi
    await client.send_video(
        chat_id=message.chat.id,
        video=anime["video"],
        caption=caption,
        reply_markup=keyboard,
    )
  else:
    await message.reply(
        "❌ Bunday kodli anime topilmadi. Boshqa kod yuborib ko'ring."
    )


async def main():
    async with app:
        print("Bot muvaffaqiyatli ishga tushdi!")
        await idle()

if __name__ == "__main__":
    app.run(main())
    
    
    
    
    
