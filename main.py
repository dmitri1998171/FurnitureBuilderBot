import telebot, json
from telebot import types

modulesCounter = 0

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
        global modulesCounter

        if(w > self.freeWidth):
            print("ERROR! Can't add a new module into the plank!")
        else:
            if(w > 0):
                self.setBusyWidth(self.busyWidth + w)
                self.modules.append(w)
                modulesCounter += 1

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
    global moduleCalcState, plankArr, width, sinkSize, cookingSize, modules, leftSpace, modulesCounter

    moduleCalcState = 0
    plankArr = []
    width = 0
    sinkSize = 0
    cookingSize = 0
    leftSpace = 0
    modulesCounter = 0
    modules = createModulesHashTable()

settings = getSettingsFromJSON()
moduleWidthes = settings['moduleWidthes']
minSize = settings['minSize']
maxSize = settings['maxSize']
plankSize = settings['plankSize']            # Длина доски (заготовки)
defaultModule = settings['defaultModule']
fillerSize = settings['fillerSize']

menuState = 0
costCalcState = 0
moduleCalcState = 0
plankArr = []

width = 0
sinkSize = 0
cookingSize = 0

modules = createModulesHashTable()
leftSpace = 0
minimumForCooking = (minSize * 2) + (plankSize - minSize)

bot = telebot.TeleBot(settings['token'])

def buttonPressedCheck(message):
    global menuState

    if(message.text == "Рассчет кол-ва модулей"):
        menuState = 1
        InitVariables()
        bot.send_message(message.chat.id, "Отправь мне ширину кухни в мм - я все посчитаю")
        return menuState

    if(message.text == "Рассчет цены"):
        menuState = 2
        InitVariables()
        bot.send_message(message.chat.id, "         ")
        return menuState
    
    return 0

@bot.message_handler(commands=['start'])
def start_message(message):
    global menuState

    menuState = 0
    InitVariables()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text= "Рассчет кол-ва модулей")
    btn2 = types.KeyboardButton(text= "Рассчет цены")
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id,"Привет ✌️ Я бот-сборщик мебели!", reply_markup=markup)

@bot.message_handler(content_types='text')
def get_text(message):
    global menuState, moduleCalcState, width, sinkSize, cookingSize, plankArr

    if(menuState == 2):
        print("menuState: ", menuState)

    if(menuState == 1):
        if(message.text.isnumeric()):
            if(moduleCalcState == 2):
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
                
            elif(moduleCalcState == 1):
                sinkSize = int(message.text)
                
                if(sinkSize < minSize or sinkSize > maxSize):
                    bot.send_message(message.chat.id, f"Неверный размер мойки\nmin: {minSize}\nmax: {maxSize}")
                elif(sinkSize > width):
                    bot.send_message(message.chat.id, f"Неверный размер мойки\nМойка больше стены!")
                else:
                    plankArr[0].addModule(sinkSize)

                    if(width >= plankSize):
                        plankArr[0].addModule(plankArr[0].getFreeWidth())
                    else:
                        plankArr[0].addModule(width - plankArr[0].getBusyWidth())

                    if(width >= minimumForCooking):
                        bot.send_message(message.chat.id,"Укажи размер плиты")
                        moduleCalcState = 2
                    else:
                        if(leftSpace > fillerSize):
                            plankArr[1].addModule(leftSpace)

                        globalCalc(message)
                        InitVariables()

            elif(moduleCalcState == 0):
                width = int(message.text)
                wallCalc(width)

                bot.send_message(message.chat.id, "Укажи размер мойки")
                moduleCalcState = 1

        else:
            if(buttonPressedCheck(message) == 0):
                bot.send_message(message.chat.id, "Это не число")

    if(menuState == 0):
        buttonPressedCheck(message)

def wallCalc(width):
    global plankArr, leftSpace

    div = width / plankSize

    if(div > 1):
        base = width // plankSize

        for i in range(base):
            plankArr.append(Plank(plankSize))

        if(div % 2 != 0):
            leftSpace = width - (base * plankSize)

            if(leftSpace > fillerSize):
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
    
    plankArrSize = len(plankArr)
    resultMessage = f'Кол-во модулей: {modulesCounter}\n\n'
    i = 0

    while i in range(plankArrSize):
        resultMessage += str(plankArr[i].getModules())

        if(i == 0):
            resultMessage += ' Мойка'
        
        if(i == 1):
            if(width >= minimumForCooking):
                resultMessage += ' Плита'

        resultMessage += '\n'
        i += 1

    if(leftSpace <= fillerSize and leftSpace > 0):
        resultMessage += f"Заглушка: {leftSpace}\n"

    bot.send_message(message.chat.id, resultMessage)
    
def showResultsInRow(message):
    global leftSpace

    resultMessage = f'Кол-во модулей: {modulesCounter}\n\n'
    plankArrSize = len(plankArr)
    i = 0

    if(modulesCounter > 2):
        resultMessage += 'Мойка        Плита\n'
        # resultMessage += '   М                 П\n'

    while i in range(plankArrSize):
        for module in plankArr[i].getModules():
            resultMessage += '[' + str(module) + ']'

        i += 1

    if(leftSpace <= fillerSize and leftSpace > 0):
        resultMessage += f"\nЗаглушка: {leftSpace}\n"

    bot.send_message(message.chat.id, resultMessage)
    
def globalCalc(message):
    moduleCalc()
    showResultsInTable(message)
    # showResultsInRow(message)

bot.infinity_polling()
