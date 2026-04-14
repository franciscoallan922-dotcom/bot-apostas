import telebot
import requests
import time
import threading
from flask import Flask
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= CONTROLE =================
jogos_enviados = set()
entradas_futebol = 0
MAX_FUTEBOL = 10

@app.route('/')
def home():
    return "Bot rodando!"

# ================= FUTEBOL =================
def analisar_futebol():
    global entradas_futebol

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers).json()
    except:
        print("Erro na API")
        return

    if "response" not in response:
        return

    for jogo in response["response"]:

        if entradas_futebol >= MAX_FUTEBOL:
            return

        fixture_id = jogo["fixture"]["id"]
        minuto = jogo["fixture"]["status"]["elapsed"]
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        gols_casa = jogo["goals"]["home"] or 0
        gols_fora = jogo["goals"]["away"] or 0

        if fixture_id in jogos_enviados:
            continue

        if minuto is None or minuto < 20:
            continue

        total_gols = gols_casa + gols_fora

        if total_gols > 2:
            continue

        # ================= ESTATÍSTICAS =================
        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"

        try:
            stats = requests.get(stats_url, headers=headers).json()
        except:
            continue

        if "response" not in stats or len(stats["response"]) < 2:
            continue

        try:
            home_stats = stats["response"][0]["statistics"]
            away_stats = stats["response"][1]["statistics"]

            def pegar(stat, lista):
                for item in lista:
                    if item["type"] == stat:
                        return item["value"] if item["value"] else 0
                return 0

            chutes_home = pegar("Shots on Goal", home_stats)
            chutes_away = pegar("Shots on Goal", away_stats)

            ataques_home = pegar("Dangerous Attacks", home_stats)
            ataques_away = pegar("Dangerous Attacks", away_stats)

            total_chutes = chutes_home + chutes_away
            total_ataques = ataques_home + ataques_away

            print(f"{casa} x {fora} | Min:{minuto} | Chutes:{total_chutes} | Ataques:{total_ataques}")

        except:
            continue

        # ================= FILTRO AJUSTADO =================
        if total_chutes >= 2 and total_ataques >= 10:

            msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ {casa} vs {fora}
⏰ Minuto: {minuto}

📊 Pressão:
• Chutes no gol: {chutes_home} x {chutes_away}
• Ataques perigosos: {ataques_home} x {ataques_away}

🔥 Leitura: Pressão ofensiva

✅ Sugestão: Over 1.5 Gols
🏟️ Casa: Superbet
"""

            try:
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
                    print("SINAL ENVIADO")
            except Exception as e:
                print("Erro Telegram:", e)

            jogos_enviados.add(fixture_id)
            entradas_futebol += 1

# ================= LOOP =================
def rodar_bot():
    while True:
        try:
            print("🔄 Rodando análise...")
            analisar_futebol()
            time.sleep(90)
        except Exception as e:
            print("Erro geral:", e)
            time.sleep(10)

# ================= START =================
threading.Thread(target=rodar_bot).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
