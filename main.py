import telebot, json

def parseJSON():
    tokens = {}

    with open("token.json", 'r') as f:
        tokens = json.load(f)

    return tokens

tokens = parseJSON()
bot = telebot.TeleBot(tokens['tg'])

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"Привет ✌️ Я бот-сборщик мебели!")
    bot.send_message(message.chat.id,"Отправь мне ширину кухни - я все посчитаю")

bot.infinity_polling()