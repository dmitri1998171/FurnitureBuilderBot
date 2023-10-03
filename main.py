import telebot, json

state = 0

width = 0
sinkSize = 0
cookingSize = 0

modules = { }
other = 0

def getSettingsFromJSON():
    settings = {}

    with open("settings.json", 'r') as f:
        settings = json.load(f)

    return settings

settings = getSettingsFromJSON()
moduleWidthes = settings['moduleWidthes']

bot = telebot.TeleBot(settings['token'])

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"Привет ✌️ Я бот-сборщик мебели!")
    bot.send_message(message.chat.id,"Отправь мне ширину кухни в мм - я все посчитаю")

@bot.message_handler(content_types='text')
def get_text(message):
    global state, width, sinkSize, cookingSize

    if(message.text.isnumeric()):
        if(state == 2):
            cookingSize = int(message.text)
            moduleCalc(width)
            # showResultsInTable(message)
            showResultsInRow(message)
            state = 0
            
        elif(state == 1):
            sinkSize = int(message.text)
            bot.send_message(message.chat.id,"Укажи размер плиты")
            state = 2

        elif(state == 0):
            width = int(message.text)
            bot.send_message(message.chat.id,"Укажи размер мойки")
            state = 1

    else:
        bot.send_message(message.chat.id,"Это не число")

def moduleCalc(width):
    global other, modules

    modules = {
        '800':0,
        '600':0,
        '400':0
    }
    other = 0
    
    cycle = True
    while cycle == True:
        if(width >= moduleWidthes[0]):
            width = width - moduleWidthes[0]
            modules['800'] = modules['800'] + 1

        elif(width >= moduleWidthes[1]):
            width = width - moduleWidthes[1]
            modules['600'] = modules['600'] + 1

        elif(width >= moduleWidthes[2]):
            width = width - moduleWidthes[2]
            modules['400'] = modules['400'] + 1

        else:
            other = width
            cycle = False

    print("modules: ", modules)
    print("other: ", other)

def showResultsInTable(message):
    global other
    resultMessage = 'Кол-во модулей\n\n'

    for item in modules:
        resultMessage += "С шириной " + item + " мм : " + str(modules[item]) + " шт.\n"

    if(other != 0):
        resultMessage += "\nПоследний модуль " + str(other) + " мм"

    bot.send_message(message.chat.id, resultMessage)
    
def showResultsInRow(message):
    global other
    resultMessage = 'Модули\n\n'

    for item in modules:
        while modules[item] > 0:
            resultMessage += item + ' '
            modules[item] -= 1

    if(other != 0):
        resultMessage += "\nПоследний модуль " + str(other) + " мм"

    bot.send_message(message.chat.id, resultMessage)
    

bot.infinity_polling()
