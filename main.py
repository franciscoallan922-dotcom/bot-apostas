import time
import telebot

TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"
CHAT_ID = 5705254146  # ⚠️ número, sem aspas

bot = telebot.TeleBot(TOKEN)

def loop():
    while True:
        try:
            bot.send_message(CHAT_ID, "🚀 BOT ONLINE")

            time.sleep(60)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

loop()
