import telebot
from telebot import types
import sqlite3
import time
import os
from flask import Flask
from threading import Thread

# --- RENDER UCHUN WEB SERVER (BOTNI UYG'OQ TUTADI) ---
app = Flask('')
@app.route('/')
def home(): return "Bot 24/7 ishlamoqda!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SOZLAMALAR ---
TOKEN = '8295176970:AAFfx-A-0QpA_el2QfduSdHboQGVA9WJd-o'
ADMIN_ID = 6952175243
MY_USER = "Jabborovv_002"
KANAL_ID = '@Qarshi_Elonlar_Rasmiy'

bot = telebot.TeleBot(TOKEN)

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('supreme_v7.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, username TEXT, ads INTEGER DEFAULT 0, balance INTEGER DEFAULT 0, status TEXT DEFAULT 'Oddiy')''')
    conn.commit()
    return conn

db = init_db()

# --- KLAVIATURA ---
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("🚀 E'lon Berish", "💎 VIP Kabinet")
    m.add("📊 Statistika", "💳 Hamyon")
    m.add("📜 Qoidalar", "👨‍💻 Bog'lanish")
    return m

# --- START (HTML REJIMIDA) ---
@bot.message_handler(commands=['start'])
def start(message):
    uid, fname = message.from_user.id, message.from_user.first_name
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?, ?, ?)", (uid, fname, message.from_user.username))
    db.commit()
    
    welcome_text = (f"🔥 <b>WELCOME TO SUPREME V7!</b>\n\n"
                    f"Assalomu alaykum, {fname}!\n"
                    f"Siz O'zbekistondagi eng kuchli e'lonlar markazidasiz.\n"
                    f"Tizim yaratuvchisi: @{MY_USER}")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")

# --- BOG'LANISH ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Bog'lanish")
def contact(message):
    m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🚀 Adminga Yozish", url=f"https://t.me/{MY_USER}"))
    bot.send_message(message.chat.id, "👨‍💻 <b>Admin bilan aloqa:</b>\n\nSavollar bo'lsa yozing.", reply_markup=m, parse_mode="HTML")

# --- KABINET ---
@bot.message_handler(func=lambda m: m.text == "💎 VIP Kabinet")
def cabinet(message):
    cursor = db.cursor()
    cursor.execute("SELECT ads, balance, status FROM users WHERE id=?", (message.from_user.id,))
    res = cursor.fetchone()
    text = (f"✨ <b>SIZNING KABINETINGIZ</b> ✨\n\n"
            f"👤 Ism: <code>{message.from_user.first_name}</code>\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n"
            f"📢 E'lonlar: <b>{res[0]} ta</b>\n"
            f"💰 Balans: <b>{res[1]} so'm</b>\n"
            f"🏆 Status: <b>{res[2]}</b>")
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- E'LON BERISH ---
@bot.message_handler(func=lambda m: m.text == "🚀 E'lon Berish")
def select_cat(message):
    m = types.InlineKeyboardMarkup(row_width=2)
    cats = ["📱 Telefon", "🚗 Avto", "🏠 Uy", "💻 Kompyuter", "📦 Boshqa"]
    for c in cats:
        m.add(types.InlineKeyboardButton(c, callback_data=f"cat_{c}"))
    bot.send_message(message.chat.id, "📦 <b>Kategoriyani tanlang:</b>", reply_markup=m, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def get_details(call):
    cat = call.data.split('_')[1]
    msg = bot.send_message(call.message.chat.id, f"📝 <b>{cat}</b> tanlandi. Mahsulot nomi, narxi va raqamingizni yozing:")
    bot.register_next_step_handler(msg, get_image, cat)

def get_image(message, cat):
    desc = message.text
    msg = bot.send_message(message.chat.id, "📸 <b>Mahsulot rasmini yuboring:</b>")
    bot.register_next_step_handler(msg, send_to_admin, cat, desc)

def send_to_admin(message, cat, desc):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ <b>Xato!</b> Rasm yuboring.")
        return
    
    m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"pub_{message.from_user.id}"))
    cap = f"🆕 <b>YANGI E'LON | #{cat}</b>\n\n📄 Ma'lumot: {desc}\n👤 Sotuvchi: @{message.from_user.username}\n📍 #Qarshi #Uzbekistan"
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=cap, reply_markup=m, parse_mode="HTML")
    bot.send_message(message.chat.id, "🚀 <b>E'lon yuborildi!</b> Tez orada kanalda chiqadi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pub_'))
def publish(call):
    uid = int(call.data.split('_')[1])
    bot.copy_message(KANAL_ID, ADMIN_ID, call.message.message_id, caption=call.message.caption, parse_mode="HTML")
    cursor = db.cursor()
    cursor.execute("UPDATE users SET ads = ads + 1 WHERE id=?", (uid,))
    db.commit()
    bot.edit_message_caption(f"{call.message.caption}\n\n✅ <b>BU E'LON KANALGA JOYLANDI</b>", ADMIN_ID, call.message.message_id, parse_mode="HTML")
    bot.send_message(uid, "🎉 <b>Tabriklaymiz!</b> E'loningiz kanalga chiqdi!")

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    print(f"⚡️ BLACK MONSTER V7.5 IS ONLINE! CREATED BY @{MY_USER}")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Xato: {e}")
            time.sleep(5)
