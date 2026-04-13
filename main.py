import telebot
import time
import threading
from flask import Flask

TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 🔹 ROTA WEB (mantém Railway vivo)
@app.route('/')
def home():
    return "Bot rodando!"

# 🔹 COMANDOS TELEGRAM
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot online!")

@bot.message_handler(func=lambda message: True)
def responder(message):
    bot.send_message(message.chat.id, f"Seu ID: {message.chat.id}")

# 🔹 LOOP DO BOT (em thread separada)
def rodar_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("Erro:", e)
            time.sleep(5)

# 🔥 INICIA TUDO
if __name__ == "__main__":
    t = threading.Thread(target=rodar_bot)
    t.start()
    app.run(host="0.0.0.0", port=8080)
