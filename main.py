import telebot
import requests
import time
import threading
from flask import Flask
import os
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "17ddec5174ecbb11adfd6fea8f212df9"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= BANCA =================
banca = 1000
lucro_dia = 0
greens = 0
reds = 0
total_entradas = 0

bot_ativo = True

jogos_enviados = set()
entradas_ativas = {}

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
    return "SNIPER ELITE ONLINE"

# ================= FUNÇÃO =================
def pegar_stat(stat, lista):
    for item in lista:
        if item["type"] == stat:
            return item["value"] if item["value"] else 0
    return 0

# ================= FUTEBOL =================
def analisar_futebol():
    global total_entradas

    if not bot_ativo:
        return

    headers = {"x-apisports-key": API_KEY}

    try:
        data = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=headers).json()
    except:
        return

    if "response" not in data:
        return

    for jogo in data["response"]:
        liga_id = jogo["league"]["id"]
        if liga_id not in LIGAS_PERMITIDAS:
            continue

        fixture_id = jogo["fixture"]["id"]
        minuto = jogo["fixture"]["status"]["elapsed"]

        if fixture_id in jogos_enviados or minuto is None:
            continue

        gols = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)
        if gols > 2:
            continue

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        liga = jogo["league"]["name"]

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

        chutes = pegar_stat("Shots on Goal", home_stats) + pegar_stat("Shots on Goal", away_stats)
        ataques = pegar_stat("Dangerous Attacks", home_stats) + pegar_stat("Dangerous Attacks", away_stats)

        xg = (chutes * 0.3) + (ataques * 0.04)

        if xg < 1.8:
            continue

        if xg >= 2.5:
            fogo = "🔥🔥🔥🔥🔥"
        else:
            fogo = "🔥🔥🔥"

        if 20 <= minuto <= 40 or 55 <= minuto <= 75:

            stake = round(banca * 0.02, 2)

            bot.send_message(CHAT_ID, f"""

⚽ SNIPER ELITE PRO

⚔️ {casa} vs {fora}
🏆 {liga}
⏰ {minuto}'

📊 Pressão:
• Chutes no gol: {chutes}
• Ataques perigosos: {ataques}

📈 xG: {round(xg,2)}

{fogo}

✅ Sugestão: Over 1.5 Gols

💰 Stake: R${stake}

""")

            jogos_enviados.add(fixture_id)
            total_entradas += 1

            entradas_ativas[fixture_id] = {
                "stake": stake
            }

# ================= BASQUETE =================
def analisar_basquete():

    headers = {"x-apisports-key": API_KEY}

    try:
        data = requests.get("https://v1.basketball.api-sports.io/games?live=all", headers=headers).json()
    except:
        return

    if "response" not in data:
        return

    for jogo in data["response"]:

        game_id = jogo["id"]

        if game_id in jogos_enviados:
            continue

        status = jogo["status"]["short"]

        if status not in ["Q3", "Q4"]:
            continue

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        pontos_casa = jogo["scores"]["home"]["points"] or 0
        pontos_fora = jogo["scores"]["away"]["points"] or 0

        total_pontos = pontos_casa + pontos_fora

        tempo = jogo["status"]["long"]

        minutos = jogo["status"]["clock"]

        try:
            minutos = int(minutos.split(":")[0])
        except:
            minutos = 30

        ritmo = total_pontos / max(minutos,1)

        proj = ritmo * 48

        linha_over = round(proj - 12)
        linha_under = round(proj + 12)

        if proj < 200:
            continue

        stake = round(banca * 0.02, 2)

        bot.send_message(CHAT_ID, f"""

🏀 SNIPER ELITE PRO MAX

⚔️ {casa} vs {fora}
⏱️ {tempo}

📊 Placar: {pontos_casa} x {pontos_fora}
📈 Ritmo: {round(ritmo,2)} pts/min

🔢 Projeção final: {round(proj)}

🎯 Linha ideal:
👉 Over {linha_over}.5
👉 Under {linha_under}.5

🔥🔥🔥🔥🔥

💰 Stake: R${stake}

""")

        jogos_enviados.add(game_id)

# ================= RESULTADOS =================
def verificar_resultados():
    global greens, reds, banca, lucro_dia

    headers = {"x-apisports-key": API_KEY}

    while True:
        try:
            for fixture_id in list(entradas_ativas.keys()):

                data = requests.get(
                    f"https://v3.football.api-sports.io/fixtures?id={fixture_id}",
                    headers=headers
                ).json()

                if "response" not in data:
                    continue

                jogo = data["response"][0]

                gols = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)
                status = jogo["fixture"]["status"]["short"]

                entrada = entradas_ativas[fixture_id]

                if gols >= 2:
                    lucro = entrada["stake"] * 0.75
                    banca += lucro
                    lucro_dia += lucro

                    bot.send_message(CHAT_ID, f"✅ GREEN +R${round(lucro,2)}")

                    greens += 1
                    del entradas_ativas[fixture_id]

                elif status == "FT":
                    banca -= entrada["stake"]
                    lucro_dia -= entrada["stake"]

                    bot.send_message(CHAT_ID, f"❌ RED -R${entrada['stake']}")

                    reds += 1
                    del entradas_ativas[fixture_id]

            time.sleep(60)

        except:
            time.sleep(10)

# ================= RELATÓRIO =================
def relatorio():
    while True:
        try:
            if datetime.now().strftime("%H:%M") == "23:59":
                taxa = (greens / total_entradas * 100) if total_entradas else 0

                bot.send_message(CHAT_ID, f"""

📊 RELATÓRIO FINAL

Entradas: {total_entradas}
Greens: {greens}
Reds: {reds}
Assertividade: {round(taxa,2)}%
Banca: R${round(banca,2)}

""")

                time.sleep(60)

            time.sleep(30)
        except:
            time.sleep(10)

# ================= HEARTBEAT =================
def heartbeat():
    while True:
        bot.send_message(CHAT_ID, "🤖 SNIPER ELITE ONLINE E FUNCIONANDO")
        time.sleep(3600)

# ================= LOOP =================
def loop():
    while True:
        analisar_futebol()
        analisar_basquete()
        time.sleep(60)

# ================= START =================
threading.Thread(target=loop).start()
threading.Thread(target=verificar_resultados).start()
threading.Thread(target=relatorio).start()
threading.Thread(target=heartbeat).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
