import telebot
import time
import threading
import requests
from flask import Flask
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ODDS_API_KEY = "ce9cc9914cdc3a7d27e30f663150addd"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ENVIADOS = set()

LIGAS_PERMITIDAS = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "Brazil Serie A",
    "Brazil Serie B"
]

@app.route('/')
def home():
    return "Bot online"

# ⏱️ FILTRO DE TEMPO (AO VIVO)
def jogo_ativo(jogo):
    try:
        agora = datetime.utcnow()
        hora_jogo = datetime.fromisoformat(jogo["commence_time"].replace("Z", ""))
        diferenca = abs((hora_jogo - agora).total_seconds())

        return diferenca <= 20000  # até 2h
    except:
        return False

# ⚽ FUTEBOL PROFISSIONAL
def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    data = requests.get(url).json()

    sinais = []

    for jogo in data:
        try:
            if not jogo_ativo(jogo):
                continue

            liga = jogo.get("sport_title", "")
            if not any(l in liga for l in LIGAS_PERMITIDAS):
                continue

            home = jogo["home_team"]
            away = jogo["away_team"]

            for book in jogo["bookmakers"]:
                for market in book["markets"]:
                    if market["key"] == "totals":

                        for o in market["outcomes"]:
                            linha = o["point"]
                            odds = o["price"]
                            tipo = o["name"]

                            if 1.50 <= odds <= 1.80:

                                # OVER 1.5
                                if tipo == "Over" and linha == 1.5:
                                    sinais.append((home, away, liga, linha, odds))

                                # UNDER 3.5+
                                if tipo == "Under" and linha >= 3.5:
                                    sinais.append((home, away, liga, linha, odds))

        except:
            continue

    return sinais

# 🏀 BASQUETE
def buscar_basquete():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    data = requests.get(url).json()

    sinais = []

    for jogo in data:
        try:
            if not jogo_ativo(jogo):
                continue

            home = jogo["home_team"]
            away = jogo["away_team"]

            for book in jogo["bookmakers"]:
                for market in book["markets"]:
                    if market["key"] == "totals":

                        for o in market["outcomes"]:
                            linha = o["point"]
                            odds = o["price"]

                            if 1.50 <= odds <= 1.75:
                                sinais.append((home, away, linha, odds))

        except:
            continue

    return sinais

# 📩 FUTEBOL MSG
def enviar_futebol(home, away, liga, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ {home} x {away}
🏆 {liga}

🎯 Entrada: Over {linha} Gols
💰 Odd: {odds}

🔥 Estratégia: Conservador Profissional
"""

    bot.send_message(CHAT_ID, msg)
    ENVIADOS.add(chave)

# 📩 BASQUETE MSG
def enviar_basquete(home, away, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
🏀 SNIPER: BASQUETE LIVE

⚔️ {home} x {away}

📊 Linha: {linha}

🔥 Entrada: Over (ritmo projetado)

💰 Odd: {odds}
"""

    bot.send_message(CHAT_ID, msg)
    ENVIADOS.add(chave)

# 🔁 LOOP PRINCIPAL
def loop():
    while True:
        try:
            futebol = buscar_futebol()
            basquete = buscar_basquete()

            for h, a, l, linha, o in futebol:
                enviar_futebol(h, a, l, linha, o)

            for h, a, linha, o in basquete:
                enviar_basquete(h, a, linha, o)

            time.sleep(90)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# 🚀 START
threading.Thread(target=loop).start()
threading.Thread(target=bot.infinity_polling).start()

app.run(host="0.0.0.0", port=8080)
