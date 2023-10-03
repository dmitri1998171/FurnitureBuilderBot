import telebot, json

moduleWidthes = [800, 600, 400]
modules = {
    '800':0,
    '600':0,
    '400':0
}
other = 0

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

@bot.message_handler(content_types='text')
def get_text(message):
    if(message.text.isnumeric()):
        moduleCalc(int(message.text))
        showResults(message)

    else:
        bot.send_message(message.chat.id,"Это не число")

def moduleCalc(width):
    cycle = True
    
    while cycle == True:
        if(width > moduleWidthes[0]):
            width = width - moduleWidthes[0]
            modules['800'] = modules['800'] + 1

        elif(width > moduleWidthes[1]):
            width = width - moduleWidthes[1]
            modules['600'] = modules['600'] + 1

        elif(width > moduleWidthes[2]):
            width = width - moduleWidthes[2]
            modules['400'] = modules['400'] + 1

        else:
            other = width
            cycle = False

    print("modules: ", modules)
    print("other: ", other)

def showResults(message):
    resultMessage = 'Кол-во модулей\n\n'

    for item in modules:
        resultMessage += "С шириной " + item + " мм : " + str(modules[item]) + " шт.\n"

    bot.send_message(message.chat.id, resultMessage)
    

bot.infinity_polling()