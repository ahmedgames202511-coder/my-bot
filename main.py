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
    markup.add("🎨 صناعة صورة (50)", "🎬 صناعة فيديو (150)")
    markup.add("💰 رصيدي والـ ID", "⚙️ لوحة المدير")
    
    # رسالة ترحيب فيها الـ ID وااااضح جداً
    msg = (f"✨ أهلاً بك يا {message.from_user.first_name}\n\n"
           f"🆔 الـ ID الخاص بك هو: {uid}\n"
           f"💰 رصيدك الحالي: {users_data[uid]} كريدت\n\n"
           "ℹ️ لزيادة رصيدك ارسل الـ ID للمدير: @AHMEDST55")
    
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي والـ ID")
def show_info(message):
    uid = message.from_user.id
    balance = users_data.get(uid, 0)
    bot.reply_to(message, f"👤 معلومات حسابك:\n\n🆔 الخاص بك: {uid}\n💰 رصيدك: {balance} كريدت")

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة (50)")
def ask_photo(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة بالإنجليزية (مثال: red car):")
        bot.register_next_step_handler(msg, generate_photo)
    else:
        bot.reply_to(message, "❌ رصيدك لا يكفي (تحتاج 50 كريدت)")

def generate_photo(message):
    uid = message.from_user.id
    prompt = message.text
    if prompt in ["🎨 صناعة صورة (50)", "🎬 صناعة فيديو (150)", "💰 رصيدي والـ ID", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري رسم صورتك... انتظر ثواني.")
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true&seed={time.time()}"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            bot.send_photo(message.chat.id, io.BytesIO(response.content), caption=f"✅ تمت الصورة!\n💰 الباقي: {users_data[uid]}")
        else: raise Exception()
    except:
        bot.reply_to(message, "⚠️ فشل السيرفر، تم إعادة الكريدت.")
        users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "🎬 صناعة فيديو (150)")
def ask_video(message):
    # حالياً فيديوهات ذكاء اصطناعي مكلفة جداً، فالبوت بيبعت رسالة توضيحية
    bot.reply_to(message, "⚠️ خدمة الفيديوهات قيد التطوير حالياً وسيتم تفعيلها قريباً بـ 150 كريدت!")

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def admin_entry(message):
    msg = bot.reply_to(message, "🔐 أدخل كلمة سر المدير:")
    bot.register_next_step_handler(msg, check_admin)

def check_admin(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً يا مدير!\nارسل الـ ID وعلامة + ثم النقاط\nمثال: 123456+500")
        bot.register_next_step_handler(msg, add_credits)
    else: bot.reply_to(message, "❌ كلمة السر خطأ!")

def add_credits(message):
    try:
        target, pts = message.text.split('+')
        t_id = int(target.strip())
        points = int(pts.strip())
        users_data[t_id] = users_data.get(t_id, 0) + points
        bot.reply_to(message, f"✅ تم شحن {points} لـ {t_id}")
        bot.send_message(t_id, f"🎉 المدير شحن لك {points} كريدت!")
    except: bot.reply_to(message, "⚠️ خطأ في التنسيق! مثال: ID+100")

if __name__ == "__main__":
    bot.infinity_polling()
    
