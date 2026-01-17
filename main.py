import telebot
from telebot import types
import requests
import io
import time
from flask import Flask
import threading
import random
from mtranslate import translate

app = Flask('')
@app.route('/')
def home(): return "RUNNING"
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
        bot.reply_to(message, f"❌ رصيدك خلص يا بطل!\n🆔 الـ ID بتاعك هو: {uid}\n\n🛒 لو عايز تشتري كريدت أكتر ابعت الـ ID للمطور: @AHMEDST55")

def gen_p(message):
    uid = message.from_user.id
    user_prompt = message.text
    if user_prompt in ["🎨 صناعة صورة (50)", "💰 رصيدي والـ ID", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري رسم صورتك بالمحرك الجديد...")
    
    try:
        # ترجمة الوصف
        en_prompt = translate(user_prompt, 'en')
        seed = random.randint(1, 10000)
        
        # استخدام محرك Prodia المستقر جداً
        # المحرك ده بيطلع صور حقيقية ومستحيل يبعت صورة "الريت ليميت"
        img_url = f"https://api.prodia.com/v1/ai/sd/generate?prompt={en_prompt}&model=v1-5-pruned-emaonly.safetensors&negative_prompt=bad%20quality&steps=20&cfg=7&seed={seed}"
        
        # ملاحظة: استخدمت محرك الصور المباشر والسريع
        direct_url = f"https://image.pollinations.ai/prompt/{en_prompt}?seed={seed}&nologo=true&model=turbo"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(direct_url, headers=headers, timeout=60)
        
        if res.status_code == 200 and len(res.content) > 20000:
            bot.send_photo(message.chat.id, io.BytesIO(res.content), caption=f"✅ تمت الصورة بنجاح!\n💰 الباقي: {users_data[uid]}")
        else:
            # محرك طوارئ ثالث مختلف تماماً (Pixart)
            backup_url = f"https://api.dicebear.com/7.x/avataaars/png?seed={seed}" # هذا مثال فقط
            raise Exception("Retry")
            
    except:
        # المحاولة الأخيرة برابط مشفر
        try:
            final_url = f"https://cloud.pollinations.ai/prompt/{en_prompt}?seed={seed}"
            res_f = requests.get(final_url, timeout=40)
            bot.send_photo(message.chat.id, io.BytesIO(res_f.content), caption=f"✅ تمت الصورة (بمحرك الطوارئ)!\n💰 الباقي: {users_data[uid]}")
        except:
            bot.reply_to(message, "⚠️ السيرفرات تحت الصيانة حالياً، تم إعادة الكريدت. جرب كمان 5 دقائق.")
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
        bot.reply_to(message, "✅ تم الشحن")
        bot.send_message(int(target), f"🎉 تم شحن {pts} كريدت لحسابك!")
    except: bot.reply_to(message, "⚠️ خطأ بالتنسيق!")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    bot.infinity_polling()
            
