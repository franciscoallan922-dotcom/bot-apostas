import telebot
import requests
import time
import threading
from flask import Flask
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_FOOTBALL = "17ddec5174ecbb11adfd6fea8f212df9"
API_ODDS = "SUA_ODDS_API_AQUI"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= CONTROLE =================
jogos_enviados = set()
entradas_futebol = 0
MAX_FUTEBOL = 10

# ================= LIGAS =================
LIGAS_PERMITIDAS = [
    39,40,41,45,48,
    140,78,135,61,66,
    88,94,
    2,3,848,
    71,72,73,
    13,11,
    1,4,5,6,
    307
]

@app.route('/')
def home():
    return "ELITE SNIPER ONLINE"

# ================= FUNÇÃO =================
def pegar_stat(stat, lista):
    for item in lista:
        if item["type"] == stat:
            return item["value"] if item["value"] else 0
    return 0

# ================= FUTEBOL =================
def analisar_futebol():
    global entradas_futebol

    headers = {"x-apisports-key": API_FOOTBALL}

    try:
        data = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=headers).json()
    except:
        return

    if "response" not in data:
        return

    for jogo in data["response"]:

        if entradas_futebol >= MAX_FUTEBOL:
            return

        liga_id = jogo["league"]["id"]
        if liga_id not in LIGAS_PERMITIDAS:
            continue

        fixture_id = jogo["fixture"]["id"]
        minuto = jogo["fixture"]["status"]["elapsed"]

        if fixture_id in jogos_enviados or minuto is None:
            continue

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        gols = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)

        if gols > 2:
            continue

        # ================= STATS =================
        try:
            stats = requests.get(
                f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}",
                headers=headers
            ).json()
        except:
            continue

        if "response" not in stats or len(stats["response"]) < 2:
            continue

        home_stats = stats["response"][0]["statistics"]
        away_stats = stats["response"][1]["statistics"]

        chutes_home = pegar_stat("Shots on Goal", home_stats)
        chutes_away = pegar_stat("Shots on Goal", away_stats)

        ataques_home = pegar_stat("Dangerous Attacks", home_stats)
        ataques_away = pegar_stat("Dangerous Attacks", away_stats)

        total_chutes = chutes_home + chutes_away
        total_ataques = ataques_home + ataques_away

        print(f"{casa} x {fora} | {minuto} | C:{total_chutes} | A:{total_ataques}")

        # ================= AJUSTE ELITE =================
        if total_ataques == 0:
            if total_chutes < 4:
                continue

        # ================= 1º TEMPO =================
        if 20 <= minuto <= 40:
            if total_chutes >= 3 or total_ataques >= 12:

                msg = f"""
⚽ SNIPER ELITE 1T

⚔️ {casa} vs {fora}
⏰ {minuto}'

📊 Pressão:
• Chutes: {chutes_home} x {chutes_away}
• Ataques: {ataques_home} x {ataques_away}

🔥 Entrada antecipada

✅ Over 1.5 Gols
"""
                bot.send_message(CHAT_ID, msg)
                jogos_enviados.add(fixture_id)
                entradas_futebol += 1

        # ================= 2º TEMPO =================
        elif 55 <= minuto <= 75:
            if total_chutes >= 4 or total_ataques >= 20:

                msg = f"""
⚽ SNIPER ELITE 2T

⚔️ {casa} vs {fora}
⏰ {minuto}'

📊 Pressão:
• Chutes: {chutes_home} x {chutes_away}
• Ataques: {ataques_home} x {ataques_away}

🔥 Gol maduro

✅ Over 1.5 Gols
"""
                bot.send_message(CHAT_ID, msg)
                jogos_enviados.add(fixture_id)
                entradas_futebol += 1

# ================= BASQUETE =================
def analisar_basquete():
    if "SUA_ODDS_API_AQUI" in API_ODDS:
        return

    try:
        data = requests.get(
            f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=totals&apiKey={API_ODDS}"
        ).json()
    except:
        return

    for jogo in data:

        if jogo["id"] in jogos_enviados:
            continue

        try:
            linha = jogo["bookmakers"][0]["markets"][0]["outcomes"][0]["point"]
        except:
            continue

        if linha and linha < 228:

            msg = f"""
🏀 SNIPER ELITE NBA

⚔️ {jogo['home_team']} vs {jogo['away_team']}

🔥 Linha com valor

✅ Over {linha} pontos
"""
            bot.send_message(CHAT_ID, msg)
            jogos_enviados.add(jogo["id"])

# ================= HEARTBEAT =================
def heartbeat():
    while True:
        try:
            msg = "🤖 SNIPER ELITE ONLINE E FUNCIONANDO"
            bot.send_message(CHAT_ID, msg)
            time.sleep(1200)  # 20 minutos
        except:
            time.sleep(60)

# ================= LOOP =================
def loop():
    while True:
        try:
            print("🚀 ELITE rodando...")
            analisar_futebol()
            analisar_basquete()
            time.sleep(60)
        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# ================= START =================
threading.Thread(target=loop).start()
threading.Thread(target=heartbeat).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
