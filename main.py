import telebot
import requests
import time
import threading
from flask import Flask
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

jogos_enviados = set()
entradas_futebol = 0
MAX_FUTEBOL = 10

@app.route('/')
def home():
    return "Bot rodando!"

def analisar_futebol():
    global entradas_futebol

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    try:
        data = requests.get(url, headers=headers).json()
    except:
        return

    if "response" not in data:
        return

    for jogo in data["response"]:

        if entradas_futebol >= MAX_FUTEBOL:
            return

        fixture_id = jogo["fixture"]["id"]
        minuto = jogo["fixture"]["status"]["elapsed"]

        if fixture_id in jogos_enviados:
            continue

        if minuto is None or minuto < 20:
            continue

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        gols = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)

        if gols > 2:
            continue

        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"

        try:
            stats = requests.get(stats_url, headers=headers).json()
        except:
            continue

        if "response" not in stats or len(stats["response"]) < 2:
            continue

        def pegar(stat, lista):
            for item in lista:
                if item["type"] == stat:
                    return item["value"] if item["value"] else 0
            return 0

        try:
            home_stats = stats["response"][0]["statistics"]
            away_stats = stats["response"][1]["statistics"]

            chutes = pegar("Shots on Goal", home_stats) + pegar("Shots on Goal", away_stats)
            ataques = pegar("Dangerous Attacks", home_stats) + pegar("Dangerous Attacks", away_stats)

        except:
            continue

        print(f"{casa} x {fora} | Min:{minuto} | Chutes:{chutes} | Ataques:{ataques}")

        # 🔥 NOVA LÓGICA (FLEXÍVEL)
        if chutes >= 2 or ataques >= 10:

            msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ {casa} vs {fora}
⏰ Minuto: {minuto}

📊 Pressão:
• Chutes no gol: {chutes}
• Ataques perigosos: {ataques}

🔥 Leitura: Pressão ofensiva

✅ Sugestão: Over 1.5 Gols
🏟️ Casa: Superbet
"""

            try:
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
                    print("SINAL ENVIADO")
            except:
                pass

            jogos_enviados.add(fixture_id)
            entradas_futebol += 1

def loop():
    while True:
        try:
            print("🔄 Analisando jogos...")
            analisar_futebol()
            time.sleep(60)
        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

threading.Thread(target=loop).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
