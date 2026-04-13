import telebot
import time
import threading
import requests
from flask import Flask
import os

# 🔐 CONFIG
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ODDS_API_KEY = "ce9cc9914cdc3a7d27e30f663150addd"
FOOTBALL_API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

greens = 0
reds = 0
ENVIADOS = {}

# 🌐 manter Railway vivo
@app.route('/')
def home():
    return "Bot online"

# 🧠 LIGAS PERMITIDAS
LIGAS_PERMITIDAS = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
    "Brazil Serie A",
    "Brazil Serie B"
]

# ⚽ FUTEBOL
def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    data = requests.get(url).json()

    sinais = []

    for jogo in data:
        try:
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

                            # 🎯 CONSERVADOR
                            if 1.50 <= odds <= 1.75:

                                # OVER seguro
                                if tipo == "Over" and linha <= 1.5:
                                    sinais.append((home, away, liga, linha, tipo, odds))

                                # UNDER seguro
                                if tipo == "Under" and linha >= 3.5:
                                    sinais.append((home, away, liga, linha, tipo, odds))

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
            home = jogo["home_team"]
            away = jogo["away_team"]

            for book in jogo["bookmakers"]:
                for market in book["markets"]:
                    if market["key"] == "totals":

                        for o in market["outcomes"]:
                            linha = o["point"]
                            odds = o["price"]
                            tipo = o["name"]

                            if 1.50 <= odds <= 1.75 and tipo == "Over":
                                sinais.append((home, away, linha, odds))

        except:
            continue

    return sinais

# 📩 ENVIO PADRÃO SNIPER
def enviar_futebol(home, away, liga, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ Jogo: {home} x {away}
🏆 Liga: {liga}
⏰ Momento: AO VIVO

🚩 Tendência: Linha {linha}

🥅 Leitura: Jogo com potencial ofensivo

✅ Sugestão:
➡️ Over {linha} Gols

💰 Odds: {odds}
🏟️ Casa: Superbet
🔥 Confiança: ALTA
"""

    bot.send_message(CHAT_ID, msg)

    ENVIADOS[chave] = {
        "tipo": "futebol",
        "linha": linha,
        "jogo": f"{home} x {away}",
        "verificado": False
    }

def enviar_basquete(home, away, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
🏀 SNIPER: BASQUETE LIVE

⚔️ Jogo: {home} x {away}
🏟️ Situação: AO VIVO

📊 Linha atual: {linha}

🔥 Análise:
Ritmo projetado acima da linha

✅ Sugestão:
➡️ Over {linha} Pontos

💰 Odds: {odds}
🏟️ Casa: Superbet
🔥 Confiança: ALTA
"""

    bot.send_message(CHAT_ID, msg)

    ENVIADOS[chave] = {
        "tipo": "basquete",
        "linha": linha,
        "jogo": f"{home} x {away}",
        "verificado": False
    }

# 🔎 RESULTADO REAL FUTEBOL
def verificar_resultados():
    global greens, reds

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": FOOTBALL_API_KEY}

    try:
        data = requests.get(url, headers=headers).json()

        for jogo in data.get("response", []):
            home = jogo["teams"]["home"]["name"]
            away = jogo["teams"]["away"]["name"]

            gols_home = jogo["goals"]["home"] or 0
            gols_away = jogo["goals"]["away"] or 0

            total = gols_home + gols_away
            status = jogo["fixture"]["status"]["short"]

            if status == "FT":
                for k, entrada in ENVIADOS.items():
                    if entrada["verificado"] == False:

                        if entrada["jogo"] == f"{home} x {away}":

                            linha = entrada["linha"]

                            if total > linha:
                                greens += 1
                                res = "✅ GREEN"
                            else:
                                reds += 1
                                res = "❌ RED"

                            bot.send_message(CHAT_ID, f"""
🏁 RESULTADO FINAL

⚔️ {home} x {away}
📈 Placar: {gols_home} x {gols_away}

{res}
""")

                            entrada["verificado"] = True

    except Exception as e:
        print(e)

# 🔁 LOOP
def loop():
    while True:
        try:
            futebol = buscar_futebol()
            basquete = buscar_basquete()

            for h, a, l, linha, tipo, o in futebol:
                enviar_futebol(h, a, l, linha, o)

            for h, a, linha, o in basquete:
                enviar_basquete(h, a, linha, o)

            verificar_resultados()

            time.sleep(60)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# 📊 RELATÓRIO
def relatorio():
    global greens, reds

    while True:
        if time.strftime("%H:%M") == "00:00":
            total = greens + reds
            taxa = round((greens / total) * 100, 2) if total else 0

            bot.send_message(CHAT_ID, f"""
📊 RELATÓRIO DO DIA

✅ Greens: {greens}
❌ Reds: {reds}
📈 Assertividade: {taxa}%
""")

            greens = 0
            reds = 0
            time.sleep(60)

        time.sleep(30)

# 🚀 THREADS
threading.Thread(target=loop).start()
threading.Thread(target=relatorio).start()
threading.Thread(target=bot.infinity_polling).start()

# 🌐 SERVER
app.run(host="0.0.0.0", port=8080)
