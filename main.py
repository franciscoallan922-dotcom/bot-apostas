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

# =========================
# FILTRO DE JOGOS ATIVOS
# =========================
def jogo_ativo(jogo):
    try:
        agora = datetime.utcnow()
        hora_jogo = datetime.fromisoformat(jogo["commence_time"].replace("Z", ""))
        return abs((hora_jogo - agora).total_seconds()) <= 10800  # 3h
    except:
        return False

# =========================
# FUTEBOL
# =========================
def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    r = requests.get(url)

    try:
        data = r.json()
    except:
        return []

    sinais = []

    for jogo in data:
        try:
            if not jogo_ativo(jogo):
                continue

            home = jogo["home_team"]
            away = jogo["away_team"]
            liga = jogo["sport_title"]

            for book in jogo.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market["key"] == "totals":

                        for o in market["outcomes"]:
                            linha = o.get("point")
                            odds = o.get("price")
                            tipo = o.get("name")

                            if odds and 1.50 <= odds <= 1.90:

                                if tipo == "Over" and linha and linha <= 2.5:
                                    sinais.append((home, away, liga, linha, odds))

        except:
            continue

    return sinais

def enviar_futebol(home, away, liga, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ Jogo: {home} vs {away}  
🏆 Liga: {liga}  
⏰ Momento: Ao vivo  

📊 Linha: Over {linha}  
🔥 Leitura: Pressão ofensiva + tendência de gols  

✅ Sugestão: Over {linha} Gols  
💰 Odd: {odds}
🏟️ Casa: Superbet
"""

    bot.send_message(CHAT_ID, msg)
    ENVIADOS.add(chave)

# =========================
# BASQUETE (SIMULADO RITMO)
# =========================
def buscar_basquete():
    # simulação leve (até você usar API melhor)
    jogos = [
        ("Phoenix Suns", "Portland Trail Blazers", 219.5, 1.72),
        ("Lakers", "Warriors", 225.5, 1.75),
    ]
    return jogos

def enviar_basquete(home, away, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
🏀 SNIPER: BASQUETE LIVE

⚔️ Confronto: {home} vs {away}  
⏱️ Momento: Meio do 3º quarto  

📊 Linha: {linha}  
🔥 Ritmo: Alto (projeção acima da linha)

✅ Sugestão: Over {linha} Pontos  
💰 Odd: {odds}
🏟️ Casa: Superbet
"""

    bot.send_message(CHAT_ID, msg)
    ENVIADOS.add(chave)

# =========================
# LOOP PRINCIPAL
# =========================
def loop():
    while True:
        try:
            print("🔄 Buscando oportunidades...")

            # FUTEBOL
            futebol = buscar_futebol()

            for home, away, liga, linha, odds in futebol:
                enviar_futebol(home, away, liga, linha, odds)

            # BASQUETE
            basquete = buscar_basquete()

            for home, away, linha, odds in basquete:
                enviar_basquete(home, away, linha, odds)

            time.sleep(120)

        except Exception as e:
            print("Erro:", e)
            time.sleep(10)

# =========================
# TELEGRAM
# =========================
def iniciar_bot():
    bot.infinity_polling()

# =========================
# THREADS
# =========================
threading.Thread(target=loop).start()
threading.Thread(target=iniciar_bot).start()

# =========================
# SERVIDOR (RAILWAY)
# =========================
app.run(host="0.0.0.0", port=8080)
