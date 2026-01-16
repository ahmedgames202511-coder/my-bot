import telebot
from telebot import types
import requests
import io
import time

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
    bot.send_message(message.chat.id, f"أهلاً يا {message.from_user.first_name}!\nرصيدك: {users_data[uid]} 💰", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة")
def ask(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 اكتب وصف الصورة (بالانجليزية):\nمثال: cat with sunglasses")
        bot.register_next_step_handler(msg, generate)
    else:
        bot.reply_to(message, "❌ رصيدك مخلص! شحن من: @AHMEDST55")

def generate(message):
    uid = message.from_user.id
    prompt = message.text
    if prompt in ["🎨 صناعة صورة", "💰 رصيدي", "⚙️ لوحة المدير"]: return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري الرسم... انتظر ثواني.")

    try:
        # رابط المحرك مع إضافة وقت عشوائي لضمان صورة جديدة
        seed = time.time()
        url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true"
        
        # محاولة تحميل الصورة فعلياً
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            photo = io.BytesIO(response.content)
            bot.send_photo(message.chat.id, photo, caption=f"✅ تمت الصورة!\n💰 الباقي: {users_data[uid]}")
        else:
            raise Exception("Error")
    except:
        bot.reply_to(message, "⚠️ السيرفر مشغول، جرب تاني كمان شوية.")
        users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def bal(message):
    bot.reply_to(message, f"💰 رصيدك: {users_data.get(message.from_user.id, 0)}")

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def adm(message):
    msg = bot.reply_to(message, "🔑 باسوورد المدير؟")
    bot.register_next_step_handler(msg, auth)

def auth(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "ابعت: ID+نقاط")
        bot.register_next_step_handler(msg, add)
    else: bot.reply_to(message, "❌ خطأ!")

def add(message):
    try:
        target, pts = message.text.split('+')
        users_data[int(target)] = users_data.get(int(target), 0) + int(pts)
        bot.reply_to(message, "تم الشحن ✅")
    except: bot.reply_to(message, "خطأ في التنسيق!")

if __name__ == "__main__":
    bot.infinity_polling()
