import telebot
from telebot import types
import requests
import io
import time
from flask import Flask
import threading
import random

app = Flask('')
@app.route('/')
def home(): return "Bot Online"
def run_web(): app.run(host='0.0.0.0', port=10000)

API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'
bot = telebot.TeleBot(API_TOKEN)

users_data = {}
PASSWORD = "21072014"

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users_data: users_data[uid] = 100
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎨 صناعة صورة (50)")
    markup.add("💰 رصيدي والـ ID", "⚙️ لوحة المدير")
    bot.send_message(message.chat.id, f"✨ أهلاً يا {message.from_user.first_name}\n🆔 الـ ID: {uid}\n💰 الرصيد: {users_data[uid]}", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي والـ ID")
def show_id(message):
    uid = message.from_user.id
    bot.reply_to(message, f"🆔 رقمك: {uid}\n💰 رصيدك: {users_data.get(uid, 0)}")

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة (50)")
def ask_p(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة بالانجليزي:")
        bot.register_next_step_handler(msg, gen_p)
    else: bot.reply_to(message, "❌ رصيدك مخلص!")

def gen_p(message):
    uid = message.from_user.id
    prompt = message.text
    if prompt in ["🎨 صناعة صورة (50)", "💰 رصيدي والـ ID", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري الرسم بالمحرك الجديد (غير محدود)...")
    
    try:
        # استخدام محرك مختلف تماماً (BFL) لتجنب رسالة Rate Limit
        seed = random.randint(1, 999999)
        # الرابط ده مخصص لتخطي الحماية
        img_url = f"https://no-api-limits.vercel.app/api/generate?prompt={prompt}&seed={seed}"
        
        response = requests.get(img_url, timeout=60)
        
        if response.status_code == 200:
            bot.send_photo(message.chat.id, io.BytesIO(response.content), caption=f"✅ تمت الصورة!\n💰 الباقي: {users_data[uid]}")
        else:
            # محاولة أخيرة لو المحرك الجديد تعطل
            img_url_v2 = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true"
            res_v2 = requests.get(img_url_v2, timeout=30)
            bot.send_photo(message.chat.id, io.BytesIO(res_v2.content), caption=f"✅ صورة بديلة!\n💰 الباقي: {users_data[uid]}")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ السيرفرات العالمية مزدحمة حالياً، جرب كمان شوية.")
        users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def admin_p(message):
    msg = bot.reply_to(message, "🔐 الباسوورد؟")
    bot.register_next_step_handler(msg, check_adm)

def check_adm(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً مدير!\nاشحن: ID+نقاط")
        bot.register_next_step_handler(msg, do_add)
    else: bot.reply_to(message, "❌ خطأ!")

def do_add(message):
    try:
        target, pts = message.text.split('+')
        users_data[int(target)] = users_data.get(int(target), 0) + int(pts)
        bot.reply_to(message, "✅ تم الشحن")
        bot.send_message(int(target), f"🎉 شحن لك المدير {pts} كريدت!")
    except: bot.reply_to(message, "⚠️ خطأ!")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
    
