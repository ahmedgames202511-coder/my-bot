import telebot
from telebot import types
import urllib.parse

# التوكن الخاص بك
API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'
bot = telebot.TeleBot(API_TOKEN)

# قاعدة بيانات مؤقتة للكريدت
users_data = {}
PASSWORD = "21072014"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # إعطاء 100 كريدت للمستخدم الجديد
    if user_id not in users_data:
        users_data[user_id] = 100
    
    msg = (f"أهلاً بك يا {message.from_user.first_name} في بوت الذكاء الاصطناعي! 🤖\n\n"
           f"💰 رصيدك الحالي: {users_data[user_id]} كريدت\n"
           f"🆔 الـ ID الخاص بك: `{user_id}`\n\n"
           "📌 نظام البوت:\n"
           "- اضغط على زر 'صناعة صورة' ثم أرسل الوصف.\n"
           "- تكلفة الصورة: 50 كريدت.\n\n"
           "💎 لشحن الرصيد كلم المدير: @AHMEDST55")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎨 صناعة صورة")
    markup.add("💰 رصيدي", "⚙️ لوحة المدير")
    
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- خطوة صناعة الصورة ---
@bot.message_handler(func=lambda message: message.text == "🎨 صناعة صورة")
def ask_for_prompt(message):
    user_id = message.from_user.id
    if users_data.get(user_id, 0) >= 50:
        msg = bot.reply_to(message, "📝 من فضلك أرسل وصف الصورة التي تريدها (بالانجليزية لنتائج أفضل):")
        bot.register_next_step_handler(msg, process_image_generation)
    else:
        bot.reply_to(message, "❌ رصيدك غير كافي (تحتاج 50 كريدت). اطلب شحن من @AHMEDST55")

def process_image_generation(message):
    user_id = message.from_user.id
    prompt = message.text
    
    # إذا أراد المستخدم إلغاء العملية أو ضغط زر آخر
    if prompt in ["🎨 صناعة صورة", "💰 رصيدي", "⚙️ لوحة المدير"]:
        bot.reply_to(message, "تم إلغاء طلب الصورة.")
        return

    users_data[user_id] -= 50
    bot.reply_to(message, f"⏳ جاري توليد صورتك لـ: ({prompt})...\nانتظر ثواني قليلة.")
    
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        # محرك توليد الصور
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        bot.send_photo(message.chat.id, image_url, 
                       caption=f"✅ تمت صناعة الصورة!\n💰 رصيدك المتبقي: {users_data[user_id]}")
    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ أثناء التوليد، تم إعادة الكريدت لحسابك.")
        users_data[user_id] += 50

# --- الأزرار الأخرى ---
@bot.message_handler(func=lambda message: message.text == "💰 رصيدي")
def check_balance(message):
    balance = users_data.get(message.from_user.id, 0)
    bot.reply_to(message, f"💰 رصيدك الحالي هو: {balance} كريدت.")

@bot.message_handler(func=lambda message: message.text == "⚙️ لوحة المدير")
def admin_login(message):
    msg = bot.reply_to(message, "🔑 أدخل كلمة سر المدير:")
    bot.register_next_step_handler(msg, process_admin_password)

def process_admin_password(message):
    if message.text == PASSWORD:
        msg = bot.reply_to(message, "✅ أهلاً يا مدير!\nأرسل الآن (ID المستخدم + عدد النقاط)\nمثال: `1234567+500`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_recharge)
    else:
        bot.reply_to(message, "❌ كلمة السر خاطئة!")

def process_recharge(message):
    try:
        target_id, amount = message.text.split('+')
        target_id = int(target_id.strip())
        amount = int(amount.strip())
        
        users_data[target_id] = users_data.get(target_id, 0) + amount
        bot.reply_to(message, f"✅ تم شحن {amount} كريدت بنجاح لـ {target_id}")
        bot.send_message(target_id, f"🎉 قام المدير بإضافة {amount} كريدت لرصيدك!")
    except:
        bot.reply_to(message, "⚠️ خطأ! أرسل التنسيق كالتالي: ID+نقاط")

if __name__ == "__main__":
    bot.infinity_polling()
        
