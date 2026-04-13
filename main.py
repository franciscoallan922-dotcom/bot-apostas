import telebot

TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot online!")

@bot.message_handler(func=lambda message: True)
def responder(message):
    bot.send_message(message.chat.id, f"Seu ID: {message.chat.id}")

print("Bot rodando...")

# 🔥 ESSA LINHA É A CHAVE
bot.infinity_polling(none_stop=True, interval=0)
