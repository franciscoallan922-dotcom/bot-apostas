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

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= BANCA =================
banca = 1000
stake = banca * 0.02

lucro_dia = 0

# ================= CONTROLE =================
jogos_enviados = set()
entradas_ativas = {}

greens = 0
reds = 0
total_entradas = 0

bot_ativo = True

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
    return "SNIPER ELITE AUTOMÁTICO"

# ================= FUNÇÃO =================
def pegar_stat(stat, lista):
    for item in lista:
        if item["type"] == stat:
            return item["value"] if item["value"] else 0
    return 0

# ================= FUTEBOL =================
def analisar_futebol():
    global total_entradas, bot_ativo

    if not bot_ativo:
        return

    headers = {"x-apisports-key": API_FOOTBALL}

    try:
        data = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=headers).json()
    except:
        return

    if "response" not in data:
        return

    for jogo in data["response"]:

        if not bot_ativo:
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

        gols_total = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)

        if gols_total > 2:
            continue

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

        if ataques == 0:
            continue

        # confiança
        if chutes >= 6 and ataques >= 25:
            confianca = "🔥🔥🔥🔥🔥 ALTA"
        else:
            confianca = "🔥🔥🔥 MÉDIA"

        if (20 <= minuto <= 40 or 55 <= minuto <= 75):
            if chutes >= 4 and ataques >= 15:

                global stake
                stake = round(banca * 0.02, 2)

                msg = f"""
⚽ SNIPER ELITE

⚔️ {casa} vs {fora}
⏰ {minuto}'

📊 Pressão:
• Chutes: {chutes}
• Ataques: {ataques}

{confianca}

💰 Stake: R${stake}
"""
                bot.send_message(CHAT_ID, msg + "\n\n")

                jogos_enviados.add(fixture_id)
                total_entradas += 1

                entradas_ativas[fixture_id] = {
                    "casa": casa,
                    "fora": fora
                }

# ================= RESULTADOS =================
def verificar_resultados():
    global greens, reds, banca, lucro_dia, bot_ativo

    headers = {"x-apisports-key": API_FOOTBALL}

    while True:
        try:
            for fixture_id in list(entradas_ativas.keys()):

                data = requests.get(
                    f"https://v3.football.api-sports.io/fixtures?id={fixture_id}",
                    headers=headers
                ).json()

                if "response" not in data or len(data["response"]) == 0:
                    continue

                jogo = data["response"][0]

                gols = (jogo["goals"]["home"] or 0) + (jogo["goals"]["away"] or 0)
                status = jogo["fixture"]["status"]["short"]

                entrada = entradas_ativas[fixture_id]

                if gols >= 2:
                    lucro = stake * 0.75
                    banca += lucro
                    lucro_dia += lucro

                    bot.send_message(CHAT_ID, f"✅ GREEN\n\n⚔️ {entrada['casa']} vs {entrada['fora']}\n💰 +R${round(lucro,2)}\n\n")

                    greens += 1
                    del entradas_ativas[fixture_id]

                elif status == "FT":
                    banca -= stake
                    lucro_dia -= stake

                    bot.send_message(CHAT_ID, f"❌ RED\n\n⚔️ {entrada['casa']} vs {entrada['fora']}\n💰 -R${stake}\n\n")

                    reds += 1
                    del entradas_ativas[fixture_id]

            # ================= STOP =================
            if lucro_dia >= 60:
                bot.send_message(CHAT_ID, f"""
🎯 META BATIDA!

💰 Lucro do dia: +R${round(lucro_dia,2)}
""")
                enviar_relatorio()
                bot_ativo = False

            if lucro_dia <= -60:
                bot.send_message(CHAT_ID, f"""
🛑 STOP LOSS

💰 Resultado: R${round(lucro_dia,2)}
""")
                enviar_relatorio()
                bot_ativo = False

            time.sleep(60)

        except:
            time.sleep(10)

# ================= RELATÓRIO =================
def enviar_relatorio():
    taxa = (greens / total_entradas * 100) if total_entradas > 0 else 0
    resultado = "POSITIVO" if lucro_dia >= 0 else "NEGATIVO"

    bot.send_message(CHAT_ID, f"""
📊 RELATÓRIO DO DIA

🎯 Entradas: {total_entradas}
✅ Greens: {greens}
❌ Reds: {reds}
📈 Assertividade: {round(taxa,2)}%
💰 Resultado: {resultado}
💵 Banca atual: R${round(banca,2)}
""")

# ================= FINAL DO DIA =================
def relatorio_final():
    while True:
        if time.strftime("%H:%M") == "00:00":
            enviar_relatorio()
        time.sleep(60)

# ================= HEARTBEAT =================
def heartbeat():
    while True:
        bot.send_message(CHAT_ID, "🤖 SNIPER ELITE ONLINE E FUNCIONANDO\n\n")
        time.sleep(1200)

# ================= LOOP =================
def loop():
    while True:
        try:
            analisar_futebol()
            time.sleep(60)
        except:
            time.sleep(10)

# ================= START =================
threading.Thread(target=loop).start()
threading.Thread(target=verificar_resultados).start()
threading.Thread(target=relatorio_final).start()
threading.Thread(target=heartbeat).start()

bot.infinity_polling()
app.run(host="0.0.0.0", port=8080)
