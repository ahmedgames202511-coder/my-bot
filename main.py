import telebot

API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً يا أحمد! أنا بوت مطور دلوقتي. جرب تكتب كلمة 'صورة'")

@bot.message_handler(func=lambda message: message.text == "صورة")
def send_photo(message):
    # بيبعت صورة عشوائية من الإنترنت
    photo_url = 'https://picsum.photos/400/300'
    bot.send_photo(message.chat.id, photo_url, caption="اتفضل دي صورة عشوائية ليك!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "لو عايزني أبعت صورة، اكتب كلمة 'صورة' بس.")

if __name__ == "__main__":
    bot.infinity_polling()
    
