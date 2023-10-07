import telebot, json

class Plank:
    def __init__(self, _busyWidth = 0):
        self.width = plankSize
        self.busyWidth = _busyWidth
        self.freeWidth = 0

    def setBusyWidth(self, w):
        self.busyWidth = w
        self.freeWidth = self.width - self.busyWidth

    def getWidth(self):
        return self.width
    
    def getBusyWidth(self):
        return self.busyWidth
    
    def getFreeWidth(self):
        return self.freeWidth


def getSettingsFromJSON():
    settings = {}

    with open("settings.json", 'r') as f:
        settings = json.load(f)

    return settings

def createModulesHashTable():
    modules = {elem: 0 for elem in moduleWidthes}
    return modules

def InitVariables():
    global state, plankArr, width, sinkSize, cookingSize, modules

    state = 0
    plankArr = []
    width = 0
    sinkSize = 0
    cookingSize = 0
    modules = createModulesHashTable()

settings = getSettingsFromJSON()
moduleWidthes = settings['moduleWidthes']
minSize = settings['minSize']
maxSize = settings['maxSize']
plankSize = settings['plankSize']            # Длина доски (заготовки)

state = 0
plankArr = []

width = 0
sinkSize = 0
cookingSize = 0

modules = createModulesHashTable()
leftSpace = 0

bot = telebot.TeleBot(settings['token'])

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"Привет ✌️ Я бот-сборщик мебели!")
    bot.send_message(message.chat.id,"Отправь мне ширину кухни в мм - я все посчитаю")
    
    InitVariables()

@bot.message_handler(content_types='text')
def get_text(message):
    global state, width, sinkSize, cookingSize, plankArr

    if(message.text.isnumeric()):
        if(state == 2):
            cookingSize = int(message.text)

            if( (cookingSize < minSize) or (cookingSize > maxSize) ):
                bot.send_message(message.chat.id, f"Неверный размер плиты\nmin: {minSize}\nmax: {maxSize}")
            elif( (plankArr[0].getWidth() + cookingSize) > width ):
                bot.send_message(message.chat.id, "Суммарная ширина мойки и плиты и отступа между ними больше стены!")
            else:
                globalCalc(message)        
                state = 0
            
        elif(state == 1):
            sinkSize = int(message.text)
            
            if(sinkSize < minSize or sinkSize > maxSize):
                bot.send_message(message.chat.id, f"Неверный размер мойки\nmin: {minSize}\nmax: {maxSize}")
            else:
                plankArr[0].setBusyWidth(sinkSize)

                if(plankArr[0].getFreeWidth() < minSize):
                    globalCalc(message)
                    state = 0
                else:
                    bot.send_message(message.chat.id,"Укажи размер плиты")
                    state = 2

        elif(state == 0):
            width = int(message.text)
            wallCalc(width)
            print("plankArr: ", plankArr)
            print("leftSpace: ", leftSpace)

            bot.send_message(message.chat.id,"Укажи размер мойки")
            state = 1

    else:
        bot.send_message(message.chat.id,"Это не число")

def wallCalc(width):
    global plankArr, leftSpace

    div = width / plankSize
    base = width // plankSize

    for i in range(base):
        plankArr.append(Plank())

    if(div % 2 != 0):
        leftSpace = width - (base * plankSize)

def moduleCalc():
    global leftSpace, modules, width

    createModulesHashTable()
    leftSpace = 0
    
    cycle = True
    while cycle == True:
        if(width < moduleWidthes[0]):
            cycle = False

        if(sinkSize >= moduleWidthes[0]):
            width = width - moduleWidthes[0]
            modules[800] += 1

        elif(width >= moduleWidthes[1]):
            width = width - moduleWidthes[1]
            modules[600] += 1

        elif(width >= moduleWidthes[2]):
            width = width - moduleWidthes[2]
            modules[400] += 1

        else:
            leftSpace = width

    print("modules: ", modules)
    print("leftSpace: ", leftSpace)

def showResultsInTable(message):
    global leftSpace
    resultMessage = 'Кол-во модулей\n\n'

    for item in modules:
        resultMessage += "С шириной " + item + " мм : " + str(modules[item]) + " шт.\n"

    if(leftSpace != 0):
        resultMessage += "\nПоследний модуль " + str(leftSpace) + " мм"

    bot.send_message(message.chat.id, resultMessage)
    
def showResultsInRow(message):
    global leftSpace
    resultMessage = 'Модули\n\n'

    for item in modules:
        while modules[item] > 0:
            resultMessage += item + ' '
            modules[item] -= 1

    if(leftSpace != 0):
        resultMessage += "\nПоследний модуль " + str(leftSpace) + " мм"

    bot.send_message(message.chat.id, resultMessage)
    
def globalCalc(message):
    pass
    # moduleCalc()
    # showResultsInTable(message)
    # showResultsInRow(message)

bot.infinity_polling()
