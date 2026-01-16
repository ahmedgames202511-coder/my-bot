import telebot
from telebot import types
import urllib.parse
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
    bot.send_message(message.chat.id, f"أهلاً بك يا {message.from_user.first_name}!\nرصيدك: {users_data[uid]} كريدت 💰\n\nاضغط على الزرار واكتب وصف الصورة بالانجليزي.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎨 صناعة صورة")
def ask(message):
    if users_data.get(message.from_user.id, 0) >= 50:
        msg = bot.reply_to(message, "📝 أرسل وصف الصورة الآن (بالانجليزية):\nمثال: a brave lion king")
        bot.register_next_step_handler(msg, generate)
    else:
        bot.reply_to(message, "❌ رصيدك غير كافي (50 كريدت مطلوب)")

def generate(message):
    uid = message.from_user.id
    prompt = message.text
    
    # التأكد إن المستخدم مبعتش زرار بدل الوصف
    if prompt in ["🎨 صناعة صورة", "💰 رصيدي", "⚙️ لوحة المدير"]:
        bot.reply_to(message, "تم إلغاء الطلب.")
        return

    users_data[uid] -= 50
    bot.reply_to(message, "⏳ جاري رسم صورتك... انتظر قليلاً.")
    
    try:
        # إضافة وقت عشوائي للرابط عشان الصورة تتغير كل مرة
        seed = int(time.time())
        encoded_prompt = urllib.parse.quote(prompt)
        # الرابط المباشر للصور
        url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        
        bot.send_photo(message.chat.id, url, caption=f"✅ تمت الصورة لـ: {prompt}\n💰 الباقي: {users_data[uid]}")
    except:
        bot.reply_to(message, "⚠️ حدث خطأ، تم إعادة الرصيد.")
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
        bot.reply_to(message, "تم الشحن بنجاح ✅")
    except: bot.reply_to(message, "خطأ! اكتبها كدة: ID+نقاط")

if __name__ == "__main__":
    bot.infinity_polling()
