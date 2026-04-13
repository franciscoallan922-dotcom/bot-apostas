import telebot
import time
import threading
import requests
from flask import Flask
import os

# 🔐 CONFIG
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

greens = 0
reds = 0

# 🌐 ROTA WEB (mantém Railway vivo)
@app.route('/')
def home():
    return "Bot rodando!"

# 🚀 COMANDO START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Bot online e funcionando!")

# 💬 RESPONDER QUALQUER MENSAGEM
@bot.message_handler(func=lambda message: True)
def responder(message):
    bot.send_message(message.chat.id, f"Seu ID: {message.chat.id}")

# 🧠 SIMULAÇÃO (depois trocamos por API real)
def analisar():
    import random
    return random.choice(["green", "red", None])

# 🔁 LOOP PRINCIPAL
def rodar_bot():
    global greens, reds
    
    while True:
        try:
            resultado = analisar()
            
            if resultado == "green":
                greens += 1
                if CHAT_ID:
                    bot.send_message(CHAT_ID, "✅ GREEN")
            
            elif resultado == "red":
                reds += 1
                if CHAT_ID:
                    bot.send_message(CHAT_ID, "❌ RED")

            time.sleep(60)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# 📊 RELATÓRIO DIÁRIO
def relatorio():
    global greens, reds
    
    while True:
        try:
            if time.strftime("%H:%M") == "00:00":
                total = greens + reds
                taxa = round((greens / total) * 100, 2) if total > 0 else 0

                msg = f"""
📊 RELATÓRIO DO DIA

✅ Greens: {greens}
❌ Reds: {reds}
📈 Assertividade: {taxa}%
"""

                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)

                greens = 0
                reds = 0
                time.sleep(60)

            time.sleep(30)

        except:
            time.sleep(10)

# 🤖 TELEGRAM (SEM THREAD DUPLICADA)
def iniciar_telegram():
    bot.infinity_polling()

# 🚀 START THREADS
threading.Thread(target=rodar_bot).start()
threading.Thread(target=relatorio).start()
threading.Thread(target=iniciar_telegram).start()

# 🌍 SERVIDOR (Railway)
app.run(host="0.0.0.0", port=8080)
