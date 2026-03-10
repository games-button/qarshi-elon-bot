import telebot
from telebot import types
import sqlite3
import time

# --- SUPREME SETTINGS ---
TOKEN = '8295176970:AAFfx-A-0QpA_el2QfduSdHboQGVA9WJd-o'
ADMIN_ID = 6952175243
MY_USER = "Jabborovv_002"
KANAL_ID = '@Qarshi_Elonlar_Rasmiy'

bot = telebot.TeleBot(TOKEN)

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('supreme_v7.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, username TEXT, ads INTEGER DEFAULT 0, balance INTEGER DEFAULT 0, status TEXT DEFAULT 'Oddiy')''')
    conn.commit()
    return conn

db = init_db()

# --- DYNAMIC KEYBOARDS ---
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🚀 E'lon Berish", "💎 VIP Kabinet")
    m.add("📊 Statistika", "💳 Hamyon")
    m.add("📜 Qoidalar", "👨‍💻 Bog'lanish")
    return m

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    uid, fname, uname = message.from_user.id, message.from_user.first_name, message.from_user.username
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?, ?, ?)", (uid, fname, uname))
    db.commit()
    
    welcome_text = (f"🔥 **WELCOME TO SUPREME V7!**\n\n"
                    f"Assalomu alaykum, {fname}!\n"
                    f"Siz O'zbekistondagi eng kuchli e'lonlar markazidasiz.\n"
                    f"Tizim yaratuvchisi: @{MY_USER}")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# --- 👨‍💻 BOG'LANISH (FULL MAX) ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Bog'lanish")
def contact(message):
    m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🚀 Adminga Yozish", url=f"https://t.me/{MY_USER}"))
    bot.send_message(message.chat.id, "👨‍💻 **Admin bilan aloqa:**\n\nSavollar va takliflar bo'lsa, pastdagi tugmani bosing.", reply_markup=m, parse_mode="Markdown")

# --- 💎 VIP KABINET ---
@bot.message_handler(func=lambda m: m.text == "💎 VIP Kabinet")
def cabinet(message):
    cursor = db.cursor()
    cursor.execute("SELECT ads, balance, status FROM users WHERE id=?", (message.from_user.id,))
    res = cursor.fetchone()
    text = (f"✨ **SIZNING KABINETINGIZ** ✨\n\n"
            f"👤 Ism: `{message.from_user.first_name}`\n"
            f"🆔 ID: `{message.from_user.id}`\n"
            f"📢 E'lonlar: **{res[0]} ta**\n"
            f"💰 Balans: **{res[1]} so'm**\n"
            f"🏆 Status: **{res[2]}**")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- E'LON BERISH (HIGH-TECH FLOW) ---
@bot.message_handler(func=lambda m: m.text == "🚀 E'lon Berish")
def select_cat(message):
    m = types.InlineKeyboardMarkup(row_width=2)
    cats = ["📱 Telefon", "🚗 Avto", "🏠 Uy", "💻 Kompyuter", "📦 Boshqa"]
    for c in cats:
        m.add(types.InlineKeyboardButton(c, callback_data=f"cat_{c}"))
    bot.send_message(message.chat.id, "📦 **Kategoriyani tanlang:**", reply_markup=m, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def get_details(call):
    cat = call.data.split('_')[1]
    msg = bot.send_message(call.message.chat.id, f"📝 **{cat}** tanlandi. Mahsulot nomi, narxi va raqamingizni yozing:")
    bot.register_next_step_handler(msg, get_image, cat)

def get_image(message, cat):
    desc = message.text
    msg = bot.send_message(message.chat.id, "📸 **Mahsulot rasmini yuboring:**")
    bot.register_next_step_handler(msg, send_to_admin, cat, desc)

def send_to_admin(message, cat, desc):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ **Xato!** Rasm yuboring.")
        return
    
    m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"pub_{message.from_user.id}"))
    cap = f"🆕 **YANGI E'LON | #{cat}**\n\n📄 Ma'lumot: {desc}\n👤 Sotuvchi: @{message.from_user.username}\n📍 #Qarshi #Uzbekistan"
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=cap, reply_markup=m, parse_mode="Markdown")
    bot.send_message(message.chat.id, "🚀 **E'lon yuborildi!** Tez orada kanalda chiqadi.")

# --- ADMIN PANEL (KANALGA JOYLASH) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('pub_'))
def publish(call):
    uid = int(call.data.split('_')[1])
    bot.copy_message(KANAL_ID, ADMIN_ID, call.message.message_id, caption=call.message.caption)
    cursor = db.cursor()
    cursor.execute("UPDATE users SET ads = ads + 1 WHERE id=?", (uid,))
    db.commit()
    bot.edit_message_caption(f"{call.message.caption}\n\n✅ **BU E'LON KANALGA JOYLANDI**", ADMIN_ID, call.message.message_id)
    bot.send_message(uid, "🎉 **Tabriklaymiz!** E'loningiz kanalga chiqdi!")

# --- BROADCAST SYSTEM (SUPREME) ---
@bot.message_handler(commands=['xabar'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(ADMIN_ID, "📢 Barcha foydalanuvchilarga yuboriladigan reklamani yozing:")
        bot.register_next_step_handler(msg, start_broadcasting)

def start_broadcasting(message):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    count = 0
    for u in users:
        try:
            bot.send_message(u[0], message.text)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ Reklama {count} ta odamga yuborildi!")

print(f"⚡️ BLACK MONSTER V7 IS ONLINE! CREATED BY @{MY_USER}")
bot.infinity_polling()
