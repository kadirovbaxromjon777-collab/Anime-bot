import asyncio, logging, sqlite3, aiohttp, random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8305229278:AAH7nV2p-MfHVwNa2w3j47eQJfYJyqnbxj0" 
ADMIN_ID = 7404935870
API_URL = "https://jikan.moe"

GENRES = {
    "action": {"name": "💥 Jangari", "id": 1}, "romance": {"name": "❤️ Romantika", "id": 22},
    "adventure": {"name": "🗺️ Sarguzasht", "id": 2}, "comedy": {"name": "😂 Komediya", "id": 4},
    "fantasy": {"name": "🔮 Fantaziya", "id": 10}, "horror": {"name": "👻 Daxshat", "id": 14}
}

bot, dp = Bot(token=BOT_TOKEN), Dispatcher()
db = sqlite3.connect("anime_bot.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, 
    lang TEXT DEFAULT 'uz', sfw TEXT DEFAULT 'true', fav_genre INTEGER DEFAULT 0
)""")
cursor.execute("CREATE TABLE IF NOT EXISTS custom_anime (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, info TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS channels (channel_id TEXT PRIMARY KEY, link TEXT)")

# Kanalingizni majburiy obunaga avtomatik qo'shish
cursor.execute("INSERT OR IGNORE INTO channels (channel_id, link) VALUES (?, ?)", ("-1003754381541", "https://t.me/Anidone_uz_animelar"))
db.commit()

class BotStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()
    waiting_for_broadcast = State()
    waiting_for_channel_id = State()
    waiting_for_channel_link = State()

async def check_sub(uid):
    cursor.execute("SELECT channel_id FROM channels")
    rows = cursor.fetchall()
    if not rows: return True
    try:
        for row in rows:
            ch_id = row[0]
            if ch_id.isdigit() or ch_id.startswith("-"): ch_id = int(ch_id)
            m = await bot.get_chat_member(chat_id=ch_id, user_id=uid)
            if m.status in ["left", "kicked"]: return False
        return True
    except: return False

def sub_kb():
    cursor.execute("SELECT link FROM channels")
    links = cursor.fetchall()
    buttons = []
    for i, row in enumerate(links, 1):
        buttons.append([InlineKeyboardButton(text=f"📢 {i}-Kanalga obuna bo'lish", url=row[0])])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def menu(is_admin=False):
    kb = [
        [KeyboardButton(text="🔎 Anime qidirish"), KeyboardButton(text="🔢 Kod bo'yicha qidirish")],
        [KeyboardButton(text="⭐ Reyting bo'yicha"), KeyboardButton(text="🎲 Tasodifiy anime")],
        [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="📣 Reklama")]
    ]
    if is_admin: kb.append([KeyboardButton(text="➕ Anime qo'shish"), KeyboardButton(text="👑 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def genre_kb(prefix="genre"):
    g = list(GENRES.values())
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=g[i]["name"], callback_data=f"{prefix}:{g[i]['id']}"),
         InlineKeyboardButton(text=g[i+1]["name"], callback_data=f"{prefix}:{g[i+1]['id']}")] for i in range(0, len(g), 2)
    ])

async def api(ep, params=None):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API_URL}/{ep}", params=params, timeout=15) as r:
                return (await r.json()).get("data", []) if r.status == 200 else []
    except: return []

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (m.from_user.id, m.from_user.username or "", m.from_user.full_name or ""))
    db.commit()
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Botdan foydalanish uchun kanallarga obuna bo'ling:", reply_markup=sub_kb())
    await m.answer(f"🎌 Xush kelibsiz!", reply_markup=menu(m.from_user.id == ADMIN_ID))

@dp.callback_query(F.data == "check_sub")
async def check_cb(call: CallbackQuery):
    if await check_sub(call.from_user.id):
        try: await call.message.delete()
        except: pass
        await call.message.answer("✅ Obuna tasdiqlandi!", reply_markup=menu(call.from_user.id == ADMIN_ID))
    else: await call.answer("❌ Hali hamma kanallarga obuna bo'lmadingiz!", show_alert=True)

@dp.message(F.text == "⚙️ Sozlamalar")
async def settings_menu(m: Message):
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Obuna bo'ling.", reply_markup=sub_kb())
    cursor.execute("SELECT lang, sfw, fav_genre FROM users WHERE user_id = ?", (m.from_user.id,))
    lang, sfw, fav_genre = cursor.fetchone()
    g_name = "Tanlanmagan"
    for k, v in GENRES.items():
        if v["id"] == fav_genre: g_name = v["name"]
    txt = f"⚙️ <b>Sozlamalar:</b>\n\n🌐 Til: <code>{lang.upper()}</code>\n🔞 Filtr: <code>{'YONIQ' if sfw == 'true' else 'OCHIQ'}</code>\n🎭 Janr: <code>{g_name}</code>"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Til", callback_data="set_lang"), InlineKeyboardButton(text="🔞 Filtr", callback_data="set_sfw")],
        [InlineKeyboardButton(text="🎭 Janr", callback_data="set_genre"), InlineKeyboardButton(text="❌ Yopish", callback_data="back")]
    ])
    await m.answer(txt, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "set_lang")
async def toggle_lang(call: CallbackQuery):
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (call.from_user.id,))
    new_lang = "en" if cursor.fetchone()[0] == "uz" else "uz"
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, call.from_user.id))
    db.commit()
    await call.answer(f"🌐 Til o'zgartirildi: {new_lang.upper()}")

@dp.callback_query(F.data == "set_sfw")
async def toggle_sfw(call: CallbackQuery):
    cursor.execute("SELECT sfw FROM users WHERE user_id = ?", (call.from_user.id,))
    new_sfw = "false" if cursor.fetchone()[0] == "true" else "true"
    cursor.execute("UPDATE users SET sfw = ? WHERE user_id = ?", (new_sfw, call.from_user.id))
    db.commit()
    await call.answer("🔞 Filtr holati o'zgartirildi!")

@dp.callback_query(F.data == "set_genre")
async def select_fav_genre(call: CallbackQuery):
    try: await call.message.delete()
    except: pass
    await call.message.answer("🎭 Sevimli janringizni tanlang:", reply_markup=genre_kb("fav"))

@dp.callback_query(F.data.startswith("fav:"))
async def save_fav_genre(call: CallbackQuery):
    g_id = int(call.data.split(":")[1])
    cursor.execute("UPDATE users SET fav_genre = ? WHERE user_id = ?", (g_id, call.from_user.id))
    db.commit()
    await call.answer("✅ Sevimli janringiz saqlandi!")

@dp.message(F.text == "🔎 Anime qidirish")
async def search_by_name_prompt(m: Message, state: FSMContext):
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Obuna bo'ling.", reply_markup=sub_kb())
    await state.set_state(BotStates.waiting_for_name)
    await m.answer("✍️ Anime nomini inglizcha kiriting:")

@dp.message(BotStates.waiting_for_name)
async def process_name_search(m: Message, state: FSMContext):
    await state.clear()
    cursor.execute("SELECT sfw FROM users WHERE user_id = ?", (m.from_user.id,))
    sfw_status = cursor.fetchone()[0]
    data = await api("anime", {"q": m.text.strip(), "limit": 10, "sfw": sfw_status})
    if not data: return await m.answer("❌ Hech narsa topilmadi.")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🎬 {a.get('title','')[:35]}", callback_data=f"an:{a['mal_id']}")] for a in data])
    await m.answer("🔎 Qidiruv natijalari:", reply_markup=kb)

@dp.message(F.text == "🔢 Kod bo'yicha qidirish")
async def search_by_code_prompt(m: Message, state: FSMContext):
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Obuna bo'ling.", reply_markup=sub_kb())
    await state.set_state(BotStates.waiting_for_code)
    await m.answer("🔢 Anime kodini kiriting:")

@dp.message(BotStates.waiting_for_code)
async def process_code_search(m: Message, state: FSMContext):
    await state.clear()
    code = m.text.strip()
    if not code.isdigit(): return await m.answer("❌ Faqat raqam kiriting!")
    cursor.execute("SELECT title, info FROM custom_anime WHERE id = ?", (int(code),))
    res = cursor.fetchone()
    if res: await m.answer(f"🎌 <b>{res[0]}</b>\n\nℹ️ Ma'lumot:\n{res[1][:3800]}", parse_mode="HTML")
    else: await m.answer("❌ Anime topilmadi.")

@dp.message(F.text == "⭐ Reyting bo'yicha")
async def top_rating(m: Message):
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Obuna bo'ling.", reply_markup=sub_kb())
    data = await api("top/anime", {"limit": 10})
    if not data: return await m.answer("❌ Ma'lumot topilmadi.")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🎬 {a.get('title','')[:35]}", callback_data=f"an:{a['mal_id']}")] for a in data])
    await m.answer("⭐ Reytingi baland animelar:", reply_markup=kb)

@dp.message(F.text == "🎲 Tasodifiy anime")
async def random_anime_genre_prompt(m: Message):
    if not await check_sub(m.from_user.id): return await m.answer("🔐 Obuna bo'ling.", reply_markup=sub_kb())
    cursor.execute("SELECT fav_genre FROM users WHERE user_id = ?", (m.from_user.id,))
    fav = cursor.fetchone()[0]
    if fav != 0: await process_anime_by_genre_id(m.chat.id, fav)
    else: await m.answer("🎭 Qaysi janrdagisini ko'rmoqchisiz?", reply_markup=genre_kb("genre"))

@dp.callback_query(F.data.startswith("genre:"))
async def process_random_by_genre(call: CallbackQuery):
    genre_id = int(call.data.split(":")[1])
    try: await call.message.delete()
    except: pass
    await process_anime_by_genre_id(call.message.chat.id, genre_id)

async def process_anime_by_genre_id(chat_id, genre_id):
    data = await api("anime", {"genres": genre_id, "limit": 25})
    if not data:
        await bot.send_message(chat_id, "❌ Bu janrda animelar topilmadi.")
        return
    a = random.choice(data)
    txt = f"🎌 <b>{a.get('title', 'Nomaʼlum')}</b>\n\n⭐ Reyting: {a.get('score', 'N/A')}\n epizodlar: {a.get('episodes', 'N/A')}\n\n{a.get('synopsis', 'Maʼlumot yoʻq')[:800]}"
    await bot.send_message(chat_id, txt, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
    
    
    
    
    
