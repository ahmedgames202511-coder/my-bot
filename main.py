import telebot
from telebot import types
import requests
import io

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
    bot.send_message(message.chat.id, f"أهلاً بك يا {message.from_user.first_name}!\nرصيدك: {users_data[uid]} كريدت 💰", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة")
def ask(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 أرسل وصف الصورة الآن (بالانجليزية):\nمثال: black cat in space")
        bot.register_next_step_handler(msg, generate)
    else:
        bot.reply_to(message, "❌ رصيدك غير كافي (تحتاج 50 كريدت)")

def generate(message):
    uid = message.from_user.id
    prompt = message.text
    
    if prompt in ["🎨 صناعة صورة", "💰 رصيدي", "⚙️ لوحة المدير"]:
        bot.reply_to(message, "تم إلغاء الطلب.")
        return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري توليد الصورة بالذكاء الاصطناعي... انتظر لحظة.")
    
    try:
        # محرك توليد الصور المباشر (أكثر استقراراً)
        image_url = f"https://image.pollinations.ai/prompt/{prompt}?nologo=true"
        
        # تحميل الصورة للتأكد من إرسالها كملف
        response = requests.get(image_url)
        if response.status_code == 200:
            photo = io.BytesIO(response.content)
            photo.name = 'image.png'
            bot.send_photo(message.chat.id, photo, caption=f"✅ تمت الصورة لـ: {prompt}\n💰 الباقي: {users_data[uid]}")
        else:
            raise Exception("Failed to load image")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ عذراً، السيرفر مشغول حالياً. تم إعادة رصيدك.")
        users_data[uid] += 50

@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def bal(message):
    bot.reply_to(message, f"💰 رصيدك الحالي: {users_data.get(message.from_user.id, 0)}")

@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة المدير")
def adm(message):
    msg = bot.reply_to(message, "🔑 اكتب باسوورد المدير:")
    bot.register_next_step_handler(msg, auth)

def auth(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً يا مدير!\nابعت: ID+نقاط")
        bot.register_next_step_handler(msg, add)
    else: bot.reply_to(message, "❌ الباسوورد غلط!")

def add(message):
    try:
        target_id, pts = message.text.split('+')
        users_data[int(target_id)] = users_data.get(int(target_id), 0) + int(pts)
        bot.reply_to(message, f"تم شحن {pts} نقطة للحساب {target_id} ✅")
    except: bot.reply_to(message, "خطأ! اكتبها كدة: ID+نقاط")

if __name__ == "__main__":
    bot.infinity_polling()
        
