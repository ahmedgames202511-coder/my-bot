import telebot
from telebot import types
import requests
import io
import time
from flask import Flask
import threading
import random
from mtranslate import translate

# سيرفر لإبقاء البوت حياً
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
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
    bot.reply_to(message, f"🆔 رقمك: {uid}\n💰 رصيدك الحالي: {users_data.get(uid, 0)}")

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة (50)")
def ask_p(message):
    uid = message.from_user.id
    if users_data.get(uid, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة بالعربي أو الإنجليزي:")
        bot.register_next_step_handler(msg, gen_p)
    else:
        # الرسالة المطلوبة عند انتهاء الكريدت
        bot.reply_to(message, f"❌ رصيدك غير كافي لشراء صورة.\n🆔 الـ ID الخاص بك: {uid}\n🛒 لشراء المزيد من الكريدت تواصل مع المطور: @AHMEDST55")

def gen_p(message):
    uid = message.from_user.id
    user_prompt = message.text
    if user_prompt in ["🎨 صناعة صورة (50)", "💰 رصيدي والـ ID", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري الرسم بالمحرك المطور...")
    
    try:
        # ترجمة الوصف
        en_prompt = translate(user_prompt, 'en')
        seed = random.randint(1, 9999999)
        
        # المحرك الأول (Flux)
        img_url = f"https://image.pollinations.ai/prompt/{en_prompt}?seed={seed}&nologo=true"
        res = requests.get(img_url, timeout=40)
        
        if res.status_code == 200:
            bot.send_photo(message.chat.id, io.BytesIO(res.content), caption=f"✅ تمت الصورة لـ: {user_prompt}\n💰 الباقي: {users_data[uid]}")
        else:
            raise Exception("Retry")
            
    except:
        # المحرك الاحتياطي (يعمل في حال فشل الأول)
        try:
            img_url_backup = f"https://pollinations.ai/p/{en_prompt}?width=1024&height=1024&seed={seed}"
            res_backup = requests.get(img_url_backup, timeout=40)
            bot.send_photo(message.chat.id, io.BytesIO(res_backup.content), caption=f"✅ تم الرسم (المحرك الاحتياطي)!\n💰 الباقي: {users_data[uid]}")
        except:
            bot.reply_to(message, "⚠️ السيرفرات العالمية مزدحمة حالياً، تم إعادة الكريدت.")
            users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def admin_p(message):
    msg = bot.reply_to(message, "🔐 باسوورد المدير؟")
    bot.register_next_step_handler(msg, check_adm)

def check_adm(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً مدير!\nاشحن كدة: ID+نقاط")
        bot.register_next_step_handler(msg, do_add)
    else: bot.reply_to(message, "❌ خطأ!")

def do_add(message):
    try:
        target, pts = message.text.split('+')
        users_data[int(target)] = users_data.get(int(target), 0) + int(pts)
        bot.reply_to(message, f"✅ تم شحن {pts} لـ {target}")
        bot.send_message(int(target), f"🎉 تم إضافة {pts} كريدت لرصيدك من قبل الإدارة!")
    except: bot.reply_to(message, "⚠️ خطأ بالتنسيق!")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    bot.infinity_polling()
        
