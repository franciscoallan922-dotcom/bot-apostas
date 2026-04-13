import telebot
import time

TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot online!")

@bot.message_handler(func=lambda message: True)
def responder(message):
    bot.send_message(message.chat.id, f"Seu ID: {message.chat.id}")

print("Bot rodando...")

# 🔥 LOOP ESTÁVEL (não crasha no Railway)
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception as e:
        print("Erro:", e)
        time.sleep(5)
