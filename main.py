import telebot

TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def responder(message):
    bot.reply_to(message, f"Seu ID: {message.chat.id}")

print("Bot rodando...")

bot.infinity_polling()
