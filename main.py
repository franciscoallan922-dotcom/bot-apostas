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
    return "Bot online 🚀"

# =========================
# FILTRO CORRETO (SÓ AO VIVO)
# =========================
def jogo_ativo(jogo):
    try:
        agora = datetime.utcnow()
        hora_jogo = datetime.fromisoformat(jogo["commence_time"].replace("Z", ""))

        diff = (agora - hora_jogo).total_seconds()

        # jogo já começou e ainda está rolando (~2h30)
        return 0 <= diff <= 9000

    except:
        return False

# =========================
# BUSCAR FUTEBOL
# =========================
def buscar_futebol():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=totals"
    
    try:
        r = requests.get(url)
        data = r.json()
    except:
        print("Erro ao buscar API")
        return []

    sinais = []

    print(f"Jogos recebidos: {len(data)}")

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

                            # filtro profissional
                            if odds and 1.50 <= odds <= 1.90:

                                if tipo == "Over" and linha and linha <= 2.5:
                                    sinais.append((home, away, liga, linha, odds))

        except:
            continue

    return sinais

# =========================
# ENVIO PROFISSIONAL
# =========================
def enviar_sinal(home, away, liga, linha, odds):
    chave = f"{home}-{away}-{linha}"

    if chave in ENVIADOS:
        return

    msg = f"""
⚽ SNIPER: OPORTUNIDADE DETECTADA

⚔️ Jogo: {home} vs {away}  
🏆 Liga: {liga}  
⏰ Status: AO VIVO  

📊 Linha: Over {linha}  
🔥 Leitura: Pressão ofensiva + tendência de gols  

✅ Sugestão: Over {linha} Gols  
💰 Odd: {odds}
🏟️ Casa: Superbet
"""

    try:
        bot.send_message(CHAT_ID, msg)
        print(f"Enviado: {home} x {away}")
        ENVIADOS.add(chave)
    except Exception as e:
        print("Erro ao enviar:", e)

# =========================
# LOOP PRINCIPAL
# =========================
def loop():
    while True:
        try:
            print("🔄 Buscando jogos AO VIVO...")

            sinais = buscar_futebol()

            if not sinais:
                print("Nenhuma oportunidade agora")

            for home, away, liga, linha, odds in sinais:
                enviar_sinal(home, away, liga, linha, odds)

            time.sleep(120)

        except Exception as e:
            print("Erro geral:", e)
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
