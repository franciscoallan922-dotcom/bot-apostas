import telebot
import time
import threading
from flask import Flask
import requests

# 🔑 CONFIG
TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"
ODDS_API_KEY = "ce9cc9914cdc3a7d27e30f663150addd"
FOOTBALL_API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CHAT_ID = None
ENVIADOS = {}
greens = 0
reds = 0

@app.route('/')
def home():
    return "Bot rodando!"

# 🔥 ATIVAR BOT
@bot.message_handler(commands=['start'])
def start(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(CHAT_ID, "🤖 BOT PROFISSIONAL ATIVADO!")

# 🔎 BUSCAR FUTEBOL (ODDS)
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

                            if 1.70 <= odds <= 2.20:
                                if tipo == "Over" and linha <= 2.5:
                                    sinais.append((home, away, linha, tipo, odds))
                                elif tipo == "Under" and linha >= 2.5:
                                    sinais.append((home, away, linha, tipo, odds))
        except:
            continue

    return sinais

# 📩 ENVIAR ENTRADA
def enviar_entrada(home, away, linha, tipo, odds):
    chave = f"{home}-{away}-{linha}-{tipo}"

    if chave not in ENVIADOS:
        msg = f"""
📊 ENTRADA CONFIRMADA

⚔️ {home} x {away}
📈 Linha: {linha}

🎯 Entrada: {tipo.upper()}

💰 Odds: {odds}
📍 Mercado: Gols
"""
        bot.send_message(CHAT_ID, msg)

        ENVIADOS[chave] = {
            "home": home,
            "away": away,
            "linha": linha,
            "tipo": tipo,
            "verificado": False
        }

# 🔎 VERIFICAR RESULTADOS (API FOOTBALL)
def verificar_resultados():
    global greens, reds

    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": FOOTBALL_API_KEY}

    try:
        data = requests.get(url, headers=headers).json()

        for jogo in data.get("response", []):
            home = jogo["teams"]["home"]["name"]
            away = jogo["teams"]["away"]["name"]

            gols_home = jogo["goals"]["home"]
            gols_away = jogo["goals"]["away"]

            total = (gols_home or 0) + (gols_away or 0)
            status = jogo["fixture"]["status"]["short"]

            if status == "FT":
                for chave, entrada in ENVIADOS.items():
                    if not entrada["verificado"]:
                        if entrada["home"] == home and entrada["away"] == away:

                            linha = entrada["linha"]
                            tipo = entrada["tipo"]

                            if tipo == "Over" and total > linha:
                                resultado = "GREEN"
                                greens += 1
                            elif tipo == "Under" and total < linha:
                                resultado = "GREEN"
                                greens += 1
                            else:
                                resultado = "RED"
                                reds += 1

                            msg = f"""
📊 RESULTADO FINAL

⚔️ {home} x {away}
🎯 Entrada: {tipo} {linha}

🏁 Placar: {gols_home} x {gols_away}

{ '✅ GREEN' if resultado == 'GREEN' else '❌ RED' }
"""
                            bot.send_message(CHAT_ID, msg)

                            entrada["verificado"] = True

    except Exception as e:
        print("Erro resultado:", e)

# 🔁 LOOP PRINCIPAL
def rodar_bot():
    while True:
        try:
            if CHAT_ID:
                sinais = buscar_futebol()

                for s in sinais:
                    enviar_entrada(*s)

                verificar_resultados()

            time.sleep(60)

        except Exception as e:
            print("Erro loop:", e)
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

# 🚀 THREADS
threading.Thread(target=rodar_bot).start()
threading.Thread(target=relatorio).start()
threading.Thread(target=bot.infinity_polling).start()

# 🌐 SERVIDOR (ANTI-CRASH)
app.run(host="0.0.0.0", port=8080)
