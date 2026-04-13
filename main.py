import telebot
import time
import threading
import requests
from flask import Flask
import os

# 🔑 CONFIG (Railway variables)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ODDS_API_KEY = "ce9cc9914cdc3a7d27e30f663150addd"
FOOTBALL_API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

ENVIADOS = {}
greens = 0
reds = 0

# 🌐 manter Railway vivo
@app.route('/')
def home():
    return "Bot rodando!"

# 🚀 start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 BOT PROFISSIONAL ATIVADO!")

# 🔎 FUTEBOL (ODDS)
def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
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

                            # 🎯 FILTRO CONSERVADOR
                            if 1.50 <= odds <= 1.75:
                                if tipo == "Over" and linha <= 2.5:
                                    sinais.append((home, away, linha, tipo, odds))
                                elif tipo == "Under" and linha >= 2.5:
                                    sinais.append((home, away, linha, tipo, odds))
        except:
            continue

    return sinais

# 🏀 BASQUETE (ODDS + PROJEÇÃO)
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

                            # 🎯 FILTRO CONSERVADOR
                            if 1.50 <= odds <= 1.75:
                                if tipo == "Over" and linha <= 230:
                                    sinais.append((home, away, linha, tipo, odds))
                                elif tipo == "Under" and linha >= 210:
                                    sinais.append((home, away, linha, tipo, odds))
        except:
            continue

    return sinais

# 📩 ENVIAR ENTRADA
def enviar(jogo, linha, tipo, odds, esporte):
    chave = f"{jogo}-{linha}-{tipo}"

    if chave not in ENVIADOS:
        msg = f"""
📊 ENTRADA DETECTADA

{esporte} {jogo}
📈 Linha: {linha}

🎯 Entrada: {tipo.upper()}

💰 Odds: {odds}
"""
        bot.send_message(CHAT_ID, msg)

        ENVIADOS[chave] = {
            "jogo": jogo,
            "linha": linha,
            "tipo": tipo,
            "verificado": False
        }

# 🔎 RESULTADO REAL (FUTEBOL)
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
                for chave, entrada in ENVIADOS.items():
                    if not entrada["verificado"]:

                        if entrada["jogo"] == f"{home} x {away}":

                            linha = entrada["linha"]
                            tipo = entrada["tipo"]

                            if tipo == "Over" and total > linha:
                                greens += 1
                                resultado = "✅ GREEN"
                            elif tipo == "Under" and total < linha:
                                greens += 1
                                resultado = "✅ GREEN"
                            else:
                                reds += 1
                                resultado = "❌ RED"

                            bot.send_message(CHAT_ID, f"""
🏁 RESULTADO FINAL

⚔️ {home} x {away}
📈 Placar: {gols_home} x {gols_away}

{resultado}
""")

                            entrada["verificado"] = True

    except Exception as e:
        print("Erro resultado:", e)

# 🔁 LOOP PRINCIPAL
def loop():
    while True:
        try:
            if CHAT_ID:
                futebol = buscar_futebol()
                basquete = buscar_basquete()

                for h, a, l, t, o in futebol:
                    enviar(f"{h} x {a}", l, t, o, "⚽")

                for h, a, l, t, o in basquete:
                    enviar(f"{h} x {a}", l, t, o, "🏀")

                verificar_resultados()

            time.sleep(60)

        except Exception as e:
            print("Erro loop:", e)
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
