import telebot
from telebot import types

API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'
bot = telebot.TeleBot(API_TOKEN)

# قاعدة بيانات مؤقتة للمستخدمين (النقاط)
users_data = {}
ADMIN_ID = None  # سيتم التعرف عليه عند إدخال الباسوورد
PASSWORD = "21072014"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = 100  # 100 كريدت هدية دخول
    
    msg = (f"أهلاً بك يا {message.from_user.first_name}!\n"
           f"رصيدك الحالي: {users_data[user_id]} كريدت.\n\n"
           "- عمل صورة: 50 كريدت\n"
           "- عمل فيديو: 150 كريدت\n"
           "لزيادة الكريدت كلم: @AHMEDST55")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("عمل صورة 🖼️", "عمل فيديو 🎬")
    markup.add("رصيدي 💰", "لوحة المدير ⚙️")
    
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "عمل صورة 🖼️")
def make_photo(message):
    user_id = message.from_user.id
    if users_data.get(user_id, 0) >= 50:
        users_data[user_id] -= 50
        bot.reply_to(message, "✅ جاري عمل الصورة... (خصم 50 كريدت)\nمتبقي معك: " + str(users_data[user_id]))
        # هنا مستقبلاً نربط ذكاء اصطناعي للصور
    else:
        bot.reply_to(message, "❌ رصيدك غير كافي! تحتاج 50 كريدت. كلم @AHMEDST55")

@bot.message_handler(func=lambda message: message.text == "عمل فيديو 🎬")
def make_video(message):
    user_id = message.from_user.id
    if users_data.get(user_id, 0) >= 150:
        users_data[user_id] -= 150
        bot.reply_to(message, "✅ جاري عمل الفيديو... (خصم 150 كريدت)\nمتبقي معك: " + str(users_data[user_id]))
    else:
        bot.reply_to(message, "❌ رصيدك غير كافي! تحتاج 150 كريدت. كلم @AHMEDST55")

@bot.message_handler(func=lambda message: message.text == "رصيدي 💰")
def check_balance(message):
    balance = users_data.get(message.from_user.id, 0)
    bot.reply_to(message, f"💰 رصيدك الحالي هو: {balance} كريدت.")

# --- قسم المدير ---
@bot.message_handler(func=lambda message: message.text == "لوحة المدير ⚙️")
def admin_panel(message):
    bot.reply_to(message, "الرجاء إدخال كلمة السر للدخول للوحة التحكم:")
    bot.register_next_step_handler(message, check_pass)

def check_pass(message):
    if message.text == PASSWORD:
        bot.reply_to(message, "✅ أهلاً أيها المدير! أرسل (ID الشخص + عدد النقاط) بهذا الشكل:\n123456+500")
        bot.register_next_step_handler(message, add_credits)
    else:
        bot.reply_to(message, "❌ كلمة سر خطأ!")

def add_credits(message):
    try:
        target_id, amount = message.text.split('+')
        target_id = int(target_id)
        amount = int(amount)
        
        if target_id in users_data:
            users_data[target_id] += amount
        else:
            users_data[target_id] = amount
            
        bot.reply_to(message, f"✅ تم إضافة {amount} كريدت للحساب {target_id}")
    except:
        bot.reply_to(message, "⚠️ خطأ في التنسيق! استعمل ID+النقاط (مثال: 112233+100)")

if __name__ == "__main__":
    bot.infinity_polling()
