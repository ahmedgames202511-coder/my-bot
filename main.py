import telebot

# التوكن بتاعك اللي بعتهولي
API_TOKEN = '8558774336:AAE_XaoYNvmRGZAeb5jdSABZDmPnr4p9Eqk'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا أحمد! البوت شغال دلوقتي بنجاح على Render 24 ساعة.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"أنت كتبت: {message.text}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
    
