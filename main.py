import telebot
from telebot import types
import requests
import io
import time
from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home(): return "OK"
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
    msg = f"✨ أهلاً يا {message.from_user.first_name}\n🆔 الـ ID بتاعك: {uid}\n💰 رصيدك: {users_data[uid]} كريدت"
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي والـ ID")
def show_id(message):
    uid = message.from_user.id
    bot.reply_to(message, f"👤 معلومات الحساب:\n🆔 رقمك: {uid}\n💰 رصيدك: {users_data.get(uid, 0)}")

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة (50)")
def ask_p(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة بالإنجليزي (مثل: spider man):")
        bot.register_next_step_handler(msg, gen_p)
    else: bot.reply_to(message, "❌ رصيدك خلص!")

def gen_p(message):
    uid = message.from_user.id
    prompt = message.text
    if prompt in ["🎨 صناعة صورة (50)", "💰 رصيدي والـ ID", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري الرسم... (قد يستغرق 10 ثواني)")
    
    # محاولة توليد الصورة
    try:
        # إضافة seed متغير عشان الصورة تطلع مختلفة كل مرة
        img_url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&seed={time.time()}"
        
        # الانتظار قليلاً لضمان استجابة السيرفر
        time.sleep(2) 
        res = requests.get(img_url, timeout=40)
        
        if res.status_code == 200:
            bot.send_photo(message.chat.id, io.BytesIO(res.content), caption=f"✅ تمت الصورة لـ: {prompt}\n💰 الباقي: {users_data[uid]}")
        else:
            raise Exception("Retry")
            
    except:
        # محاولة ثانية بمحرك احتياطي لو الأول فشل
        try:
            time.sleep(3)
            img_url_backup = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&nologo=true"
            res_backup = requests.get(img_url_backup, timeout=40)
            bot.send_photo(message.chat.id, io.BytesIO(res_backup.content), caption=f"✅ تمت الصورة (محاولة ثانية)!\n💰 الباقي: {users_data[uid]}")
        except:
            bot.reply_to(message, "⚠️ السيرفر عليه ضغط كبير، جرب كمان دقيقة. (تم إعادة الكريدت)")
            users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def admin_p(message):
    msg = bot.reply_to(message, "🔐 أدخل الباسوورد:")
    bot.register_next_step_handler(msg, check_adm)

def check_adm(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً يا مدير!\nاشحن كدة: ID+نقاط")
        bot.register_next_step_handler(msg, do_add)
    else: bot.reply_to(message, "❌ خطأ!")

def do_add(message):
    try:
        target, pts = message.text.split('+')
        users_data[int(target)] = users_data.get(int(target), 0) + int(pts)
        bot.reply_to(message, "✅ تم الشحن بنجاح")
        bot.send_message(int(target), f"🎉 شحن لك المدير {pts} كريدت!")
    except: bot.reply_to(message, "⚠️ خطأ بالتنسيق!")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
            
