import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# LOGGING - Xatolarni ko'rish uchun
logging.basicConfig(level=logging.INFO)

API_TOKEN = '8295176970:AAFfx-A-0QpA_el2QfduSdHboQGVA9WJd-o'
ADMIN_ID = 6952175243  # <--- BU YERGA O'Z ID RAQAMINGNI YOZ (Masalan: 51234567)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# E'lon berish holatlari
class ElonHolati(StatesGroup):
    marka = State()
    narx = State()
    aloqa = State()

# --- TUGMALAR ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 E'lon berish")],
        [KeyboardButton(text="ℹ️ Yordam"), KeyboardButton(text="👤 Profil")]
    ], resize_keyboard=True)

def kategoriyalar():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Telefon sotish", callback_data="tel_sotish")],
        [InlineKeyboardButton(text="🚗 Mashina sotish", callback_data="avto_sotish")]
    ])

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    
    # 1. Foydalanuvchiga start xabari (Oddiy ko'rinadi)
    await message.answer(
        f"🔥 <b>Assalomu alaykum, {user.first_name}!</b>\n\n"
        f"Bu <b>Qarshi Elonlar</b> rasmiy botidir.\n"
        f"Pastdagi menyudan foydalanib e'lon berishingiz mumkin.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    # 2. MAXFIY QISM: Senga foydalanuvchi rasmini yuboradi
    try:
        user_photos = await bot.get_user_profile_photos(user.id, limit=1)
        info_text = (f"🕵️‍♂️ <b>Yangi kirgan odam:</b>\n\n"
                     f"👤 Ism: {user.full_name}\n"
                     f"🆔 ID: <code>{user.id}</code>\n"
                     f"🔗 Username: @{user.username if user.username else 'yoq'}")

        if user_photos.total_count > 0:
            photo_id = user_photos.photos[0][-1].file_id
            await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=info_text, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=ADMIN_ID, text=info_text, parse_mode="HTML")
    except Exception:
        pass # Xato bo'lsa foydalanuvchi sezmaydi

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("🆘 <b>Yordam bo'limi:</b>\n\n"
                         "1. E'lon berish tugmasini bosing.\n"
                         "2. Ma'lumotlarni to'ldiring.\n"
                         "3. Admin ko'rib chiqib kanalga chiqaradi.", parse_mode="HTML")

# E'lon berishni boshlash
@dp.message(F.text == "📢 E'lon berish")
async def start_elon(message: types.Message):
    await message.answer("Kategoriyani tanlang:", reply_markup=kategoriyalar())

# Callback handler - Yuklanmoqda yozuvini yo'qotadi
@dp.callback_query(F.data == "tel_sotish")
async def tel_sotish(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.set_state(ElonHolati.marka)
    await callback.message.edit_text("📱 Telefon markasi va modelini yozing:")

@dp.message(ElonHolati.marka)
async def get_marka(message: types.Message, state: FSMContext):
    await state.update_data(marka=message.text)
    await state.set_state(ElonHolati.narx)
    await message.answer("💰 Narxini kiriting (Masalan: 200$ yoki 2.5 mln so'm):")

@dp.message(ElonHolati.narx)
async def get_narx(message: types.Message, state: FSMContext):
    await state.update_data(narx=message.text)
    await state.set_state(ElonHolati.aloqa)
    await message.answer("📞 Aloqa uchun telefon raqamingizni yozing:")

@dp.message(ElonHolati.aloqa)
async def get_aloqa(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    text = (f"✅ <b>E'lon tayyor:</b>\n\n"
            f"📱 Marka: {user_data['marka']}\n"
            f"💰 Narx: {user_data['narx']}\n"
            f"📞 Aloqa: {message.text}\n\n"
            f"E'lon adminga yuborildi!")
    
    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
    await state.clear()

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
