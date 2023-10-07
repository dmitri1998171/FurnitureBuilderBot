import telebot, json

class Plank:
    def __init__(self, _width = 0, _busyWidth = 0):
        self.width = _width
        self.busyWidth = _busyWidth
        self.freeWidth = self.width
        self.modules = []

    def setBusyWidth(self, w):
        self.busyWidth = w
        self.freeWidth = self.width - self.busyWidth

    def getWidth(self):
        return self.width
    
    def getBusyWidth(self):
        return self.busyWidth
    
    def getFreeWidth(self):
        return self.freeWidth
    
    def addModule(self, w):
        if(w > self.freeWidth):
            print("ERROR! Can't add a new module into the plank!")
        else:
            if(w > 0):
                self.setBusyWidth(self.busyWidth + w)
                self.modules.append(w)

    def getModules(self):
        return self.modules


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
defaultModule = settings['defaultModule']

state = 0
plankArr = []

width = 0
sinkSize = 0
cookingSize = 0

modules = createModulesHashTable()
leftSpace = 0
minimumForCooking = (minSize * 2) + (plankSize - minSize)

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
                plankArr[1].addModule(cookingSize)
                plankArr[1].addModule(plankArr[1].getFreeWidth())
                globalCalc(message)
                InitVariables()
            
        elif(state == 1):
            sinkSize = int(message.text)
            
            if(sinkSize < minSize or sinkSize > maxSize):
                bot.send_message(message.chat.id, f"Неверный размер мойки\nmin: {minSize}\nmax: {maxSize}")
            else:
                plankArr[0].addModule(sinkSize)
                plankArr[0].addModule(plankArr[0].getFreeWidth())

                if(width >= minimumForCooking):
                    bot.send_message(message.chat.id,"Укажи размер плиты")
                    state = 2
                else:
                    if(leftSpace != 0):
                        plankArr[1].addModule(leftSpace)

                    globalCalc(message)
                    InitVariables()

        elif(state == 0):
            width = int(message.text)
            wallCalc(width)

            print("plankArr size: ", len(plankArr))
            print("plankArr: ", len(plankArr) * plankSize)
            print("leftSpace: ", leftSpace)
            print()

            bot.send_message(message.chat.id,"Укажи размер мойки")
            state = 1

    else:
        bot.send_message(message.chat.id,"Это не число")

def wallCalc(width):
    global plankArr, leftSpace

    div = width / plankSize

    if(div > 1):
        base = width // plankSize

        for i in range(base):
            plankArr.append(Plank(plankSize))

        if(div % 2 != 0):
            leftSpace = width - (base * plankSize)
            plankArr.append(Plank(leftSpace))
    else:
        plankArr.append(Plank(plankSize))

def moduleCalc():
    global leftSpace, modules, width

    createModulesHashTable()
    i = 2

    while i in range(len(plankArr)):
        if(plankArr[i].getWidth() < minSize):
                plankArr[i].addModule(plankArr[i].getWidth())
        else:
            while plankArr[i].getFreeWidth() >= minSize:
                plankArr[i].addModule(defaultModule)

            if(plankArr[i].getFreeWidth() > 0):
                plankArr[i].addModule(plankArr[i].getFreeWidth())

        i += 1

def showResultsInTable(message):
    global leftSpace
    
    totalSize = len(plankArr)
    resultMessage = f'Кол-во модулей: {totalSize}\n\n'

    i = 0
    while i in range(totalSize):
        resultMessage += str(plankArr[i].getModules())

        if(i == 0):
            resultMessage += ' Мойка'
        
        if(i == 1):
            if(width >= minimumForCooking):
                resultMessage += ' Плита'

        resultMessage += '\n'
        i += 1

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
    moduleCalc()
    showResultsInTable(message)
    # showResultsInRow(message)

bot.infinity_polling()
