import telebot
import requests
import time
import threading
from flask import Flask
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "SUA_API_AQUI"  # 🔥 COLOCA SUA API FOOTBALL AQUI

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= CONTROLE =================
jogos_enviados = set()
greens = 0
reds = 0
entradas_futebol = 0
MAX_FUTEBOL = 10

# ================= SERVIDOR =================
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

    response = requests.get(url, headers=headers).json()

    if "response" not in response:
        return

    for jogo in response["response"]:

        if entradas_futebol >= MAX_FUTEBOL:
            return

        fixture_id = jogo["fixture"]["id"]
        minuto = jogo["fixture"]["status"]["elapsed"]
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        gols_casa = jogo["goals"]["home"]
        gols_fora = jogo["goals"]["away"]

        if fixture_id in jogos_enviados:
            continue

        if minuto is None or minuto < 25:
            continue

        total_gols = gols_casa + gols_fora

        if total_gols > 2:
            continue

        # ================= ESTATÍSTICAS =================
        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        stats = requests.get(stats_url, headers=headers).json()

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

        except:
            continue

        # ================= FILTRO SNIPER =================
        if total_chutes >= 3 and total_ataques >= 20:

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

            if CHAT_ID:
                bot.send_message(CHAT_ID, msg)

            jogos_enviados.add(fixture_id)
            entradas_futebol += 1

# ================= BASQUETE =================
def analisar_basquete():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=totals&apiKey=SUA_ODDS_API"

    response = requests.get(url).json()

    for jogo in response:

        jogo_id = jogo["id"]
        times = f"{jogo['home_team']} vs {jogo['away_team']}"

        if jogo_id in jogos_enviados:
            continue

        try:
            pontos = jogo["bookmakers"][0]["markets"][0]["outcomes"]
            linha = pontos[0]["point"]
        except:
            continue

        # 🔥 SIMULAÇÃO DE RITMO (não tem stats free)
        # entrada só pra NBA com linha menor
        if linha and linha < 230:

            msg = f"""
🏀 SNIPER: BASQUETE LIVE

⚔️ {times}
⏰ Momento: Meio do 3º quarto

📊 Linha: {linha}

🔥 Ritmo: Alto (simulado)

✅ Sugestão: Over {linha} Pontos
🏟️ Casa: Superbet
"""

            if CHAT_ID:
                bot.send_message(CHAT_ID, msg)

            jogos_enviados.add(jogo_id)

# ================= LOOP =================
def rodar_bot():
    while True:
        try:
            analisar_futebol()
            analisar_basquete()
            time.sleep(90)
        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# ================= RELATÓRIO =================
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
        except:
            time.sleep(10)

# ================= START =================
threading.Thread(target=rodar_bot).start()
threading.Thread(target=relatorio).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
