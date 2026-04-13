import requests
import time
import telebot

# 🔑 SEU TOKEN E CHAT_ID DIRETO (SEM ERRO)
TOKEN = "8642961399:AAEtPcccUwt93IBVYEwBZAh0YcmoV6AxoZY"
CHAT_ID = "5705254146"

bot = telebot.TeleBot(TOKEN)

greens = 0
reds = 0

def analisar_jogo(pontos, tempo):
    ritmo = pontos / tempo

    if ritmo > 2.2:
        return "OVER"
    elif ritmo < 1.8:
        return "UNDER"
    else:
        return None

def enviar_alerta(tipo, jogo):
    global greens, reds

    msg = f"📊 Entrada detectada\n\n🏀 Jogo: {jogo}\n👉 Sugestão: {tipo}"
    
    try:
        bot.send_message(CHAT_ID, msg)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def simular_resultado():
    import random
    return random.choice(["green", "red"])

def loop():
    global greens, reds

    # 🚀 AVISA QUE LIGOU
    try:
        bot.send_message(CHAT_ID, "🚀 BOT ONLINE")
    except Exception as e:
        print("Erro inicial:", e)

    while True:
        try:
            pontos = 120
            tempo = 48

            resultado = analisar_jogo(pontos, tempo)

            if resultado:
                enviar_alerta(resultado, "Jogo Exemplo")

                res = simular_resultado()

                if res == "green":
                    greens += 1
                    bot.send_message(CHAT_ID, "✅ GREEN")
                else:
                    reds += 1
                    bot.send_message(CHAT_ID, "❌ RED")

            time.sleep(60)

        except Exception as e:
            print("Erro no loop:", e)
            time.sleep(10)

loop()
