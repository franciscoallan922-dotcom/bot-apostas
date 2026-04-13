import requests
import time
import telebot

TOKEN = "SEU_TOKEN_TELEGRAM"
CHAT_ID = "SEU_CHAT_ID"

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
    bot.send_message(CHAT_ID, msg)

def simular_resultado():
    import random
    return random.choice(["green", "red"])

def loop():
    global greens, reds
    
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
            print(e)

def relatorio():
    bot.send_message(CHAT_ID, f"📊 RELATÓRIO\n\n✅ Greens: {greens}\n❌ Reds: {reds}")

loop()
