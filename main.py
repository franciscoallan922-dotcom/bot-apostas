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

@app.route('/')
def home():
    return "Bot online"

def jogo_ativo(jogo):
    try:
        agora = datetime.utcnow()
        hora_jogo = datetime.fromisoformat(jogo["commence_time"].replace("Z", ""))
        return abs((hora_jogo - agora).total_seconds()) <= 14400  # 4h
    except:
        return False

def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    r = requests.get(url)

    try:
        data = r.json()
    except:
        return []

    sinais = []

    print("Jogos recebidos:", len(data))

    for jogo in data:
        try:
            if not jogo_ativo(jogo):
                continue

            home = jogo["home_team"]
            away = jogo["away_team"]

            for book in jogo.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market["key"] == "totals":

                        for o in market["outcomes"]:
                            linha = o.get("point")
                            odds = o.get("price")
                            tipo = o.get("name")

                            # filtro balanceado
                            if odds and 1.40 <= odds <= 1.90:

                                if tipo == "Over" and linha and linha <= 2.5:
                                    sinais.append((home, away, linha, odds))

        except:
            continue

    return sinais

def enviar(jogo, linha, odds):
    chave = f"{jogo}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
⚽ SNIPER

⚔️ {jogo}
🎯 Over {linha}
💰 Odd: {odds}
"""

    bot.send_message(CHAT_ID, msg)
    ENVIADOS.add(chave)

def loop():
    while True:
        try:
            print("RODANDO LOOP...")

            sinais = buscar_futebol()

            if not sinais:
                print("Nenhum sinal encontrado")

            for home, away, linha, odds in sinais:
                enviar(f"{home} x {away}", linha, odds)

            time.sleep(120)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

def iniciar_bot():
    bot.infinity_polling()

threading.Thread(target=loop).start()
threading.Thread(target=iniciar_bot).start()

app.run(host="0.0.0.0", port=8080)
