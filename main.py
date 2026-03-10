import telebot
from telebot import types
import sqlite3
import time
import os
from flask import Flask
from threading import Thread

# --- RENDER UCHUN WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "⚡️ Black Monster V8 is Live!"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ASOSIY SOZLAMALAR ---
TOKEN = '8295176970:AAFfx-A-0QpA_el2QfduSdHboQGVA9WJd-o'
ADMIN_ID = 6952175243
MY_USER = "Jabborovv_002"
KANAL_ID = '@Qarshi_Elonlar_Rasmiy'

bot = telebot.TeleBot(TOKEN)

# --- MA'LUMOTLAR BAZASI ---
def init_db():
    conn = sqlite3.connect('supreme_v8.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, username TEXT, ads INTEGER DEFAULT 0, balance INTEGER DEFAULT 0, status TEXT DEFAULT 'Oddiy')''')
    conn.commit()
    return conn

db = init_db()

# --- ASOSIY MENYU (REPLY KEYBOARD) ---
def main_menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(types.KeyboardButton("🚀 E'lon Berish"), types.KeyboardButton("💎 VIP Kabinet"))
    m.add(types.KeyboardButton("📊 Statistika"), types.KeyboardButton("💳 Hamyon"))
    m.add(types.KeyboardButton("📜 Qoidalar"), types.KeyboardButton("👨‍💻 Bog'lanish"))
    return m

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    fname = message.from_user.first_name
    uname = message.from_user.username or "aniqlanmagan"
    
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?, ?, ?)", (uid, fname, uname))
    db.commit()
    
    welcome_text = (
        f"🔥 <b>ASSALOMU ALAYKUM, {fname.upper()}!</b>\n\n"
        f"<b>Qarshi Elonlar Rasmiy</b> botiga xush kelibsiz!\n"
        f"Bu yerda e'lon berish tez va juda oson.\n\n"
        f"🔹 <i>Yaratuvchi:</i> @{MY_USER}\n"
        f"🔹 <i>Rasmiy kanal:</i> {KANAL_ID}"
    )
    
    # Rasm bilan start berish (agar rasming bo'lsa URL qo'yishing mumkin)
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="HTML")

# --- KABINET QISMI ---
@bot.message_handler(func=lambda m: m.text == "💎 VIP Kabinet")
def cabinet(message):
    cursor = db.cursor()
    cursor.execute("SELECT ads, balance, status FROM users WHERE id=?", (message.from_user.id,))
    res = cursor.fetchone()
    
    text = (
        f"✨ <b>SIZNING SHAXSIY KABINETINGIZ</b> ✨\n\n"
        f"👤 <b>Foydalanuvchi:</b> <code>{message.from_user.first_name}</code>\n"
        f"🆔 <b>Sizning ID:</b> <code>{message.from_user.id}</code>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"📢 <b>Jami e'lonlar:</b> {res[0]} ta\n"
        f"💰 <b>Balansingiz:</b> {res[1]:,} so'm\n"
        f"🏆 <b>Status:</b> <b>{res[2]}</b>"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- BOG'LANISH ---
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Bog'lanish")
def contact(message):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🚀 Adminga Yozish", url=f"https://t.me/{MY_USER}"))
    bot.send_message(message.chat.id, "<b>Savollaringiz bormi? Admin bilan bog'laning:</b>", reply_markup=m, parse_mode="HTML")

# --- STATISTIKA ---
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats(message):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    text = (
        f"📊 <b>BOT STATISTIKASI</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users} ta\n"
        f"📢 <b>Kanalimiz:</b> {KANAL_ID}\n"
        f"🌐 <b>Hudud:</b> Qarshi, Qashqadaryo"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- QOIDALAR ---
@bot.message_handler(func=lambda m: m.text == "📜 Qoidalar")
def rules(message):
    text = (
        "📜 <b>E'LON BERISH QOIDALARI:</b>\n\n"
        "1. Haqoratli so'zlar ishlatish taqiqlanadi.\n"
        "2. Noto'g'ri ma'lumot berish mumkin emas.\n"
        "3. Har bir e'longa kamida bitta rasm bo'lishi shart.\n"
        "4. Takroriy e'lonlar o'chirib tashlanadi."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# --- E'LON BERISH TIZIMI ---
@bot.message_handler(func=lambda m: m.text == "🚀 E'lon Berish")
def start_ads(message):
    m = types.InlineKeyboardMarkup(row_width=2)
    cats = ["📱 Telefon", "🚗 Avto", "🏠 Uy", "💻 Kompyuter", "📦 Boshqa"]
    buttons = [types.InlineKeyboardButton(c, callback_data=f"cat_{c}") for c in cats]
    m.add(*buttons)
    bot.send_message(message.chat.id, "📦 <b>Kategoriyani tanlang:</b>", reply_markup=m, parse_mode="HTML")

# (Qolgan e'lon qabul qilish funksiyalari avvalgidek qoladi...)

# --- INFINITY POLLING ---
if __name__ == "__main__":
    keep_alive()
    print(f"⚡️ BLACK MONSTER V8 IS ONLINE! CREATED BY @{MY_USER}")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            time.sleep(5)
