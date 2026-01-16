import telebot
from telebot import types
import requests
import io
import time

# التوكن بتاعك
API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'
bot = telebot.TeleBot(API_TOKEN)

users_data = {}
PASSWORD = "21072014"

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users_data: users_data[uid] = 100
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎨 صناعة صورة")
    markup.add("💰 رصيدي", "⚙️ لوحة المدير")
    
    # إظهار الـ ID بوضوح في رسالة الترحيب
    msg = (f"أهلاً يا {message.from_user.first_name}!\n\n"
           f"💰 رصيدك: {users_data[uid]} كريدت\n"
           f"🆔 الـ ID الخاص بك: `{uid}`\n\n"
           "ارسل الـ ID للمدير إذا أردت شحن رصيدك.")
    
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة")
def ask(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة بالانجليزية الآن:")
        bot.register_next_step_handler(msg, generate)
    else:
        bot.reply_to(message, "❌ رصيدك مخلص! اطلب شحن من @AHMEDST55")

def generate(message):
    uid = message.from_user.id
    prompt = message.text
    if prompt in ["🎨 صناعة صورة", "💰 رصيدي", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري رسم صورتك...")

    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&seed={time.time()}"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            photo = io.BytesIO(response.content)
            bot.send_photo(message.chat.id, photo, caption=f"✅ تمت الصورة لـ: {prompt}\n💰 الباقي: {users_data[uid]}")
        else:
            raise Exception("Failed")
    except:
        bot.reply_to(message, "⚠️ السيرفر مشغول، جرب تاني.")
        users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def bal(message):
    uid = message.from_user.id
    # إظهار الـ ID هنا أيضاً لتسهيل النسخ
    bot.reply_to(message, f"💰 رصيدك الحالي: {users_data.get(uid, 0)}\n🆔 الـ ID الخاص بك: `{uid}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def adm(message):
    msg = bot.reply_to(message, "🔑 باسوورد المدير؟")
    bot.register_next_step_handler(msg, auth)

def auth(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً يا مدير!\nابعت: ID+نقاط (مثال: 12345+500)")
        bot.register_next_step_handler(msg, add)
    else: bot.reply_to(message, "❌ خطأ!")

def add(message):
    try:
        target, pts = message.text.split('+')
        target_id = int(target.strip())
        points = int(pts.strip())
        users_data[target_id] = users_data.get(target_id, 0) + points
        bot.reply_to(message, f"تم شحن {points} نقطة للحساب `{target_id}` ✅", parse_mode="Markdown")
        bot.send_message(target_id, f"🎉 تم إضافة {points} كريدت لرصيدك!")
    except:
        bot.reply_to(message, "خطأ! اكتبها كدة: ID+نقاط")

if __name__ == "__main__":
    bot.infinity_polling()
    
