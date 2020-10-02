# - *- coding: utf- 8 - *-
import sqlite3
import telebot
import random
import config
import schedule
from threading import Timer
from telebot import types
bot=telebot.TeleBot(config.TOKEN)
#bot=telebot.AsyncTeleBot(TOKEN)
connLocal = sqlite3.connect("not_mat_database.db", check_same_thread=False)
curLocal = connLocal.cursor() # Создаем курсор в бд
curLocal.execute("CREATE TABLE IF NOT EXISTS Settings_Not_Mat (ChatID int8 NOT NULL, Check_Mat boolean)")
connLocal.commit() #Сохраняем данные в бд
curLocal.execute("CREATE TABLE IF NOT EXISTS Data_List_Not_Mat (Mat_word varchar(100))")
connLocal.commit() #Сохраняем данные в бд
curLocal.execute("CREATE TABLE IF NOT EXISTS Data_Users_Not_Mat (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, ChatID int8 NOT NULL, UserID int NOT NULL, FirstName varchar(100), LastName varchar(100), Username varchar(100), Swearing int)")
connLocal.commit() #Сохраняем данные в бд
curLocal.close() #Удаляем указатель

class InfiniteTimer():
    """A Timer class that does not stop, unless you want it to."""

    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue: # Code could have been running when cancel was called.
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            print("Timer already started or running, please wait if you're restarting.")

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False # Just in case thread is running and cancel fails.
            self.thread.cancel()
        else:
            print("Timer never started or failed to initialize.")


def registration(message):
   curLocal = connLocal.cursor() # Создаем курсор в бд
   #Проверяем запись на наличие в базе данных
   curLocal.execute("SELECT * FROM Data_Users_Not_Mat WHERE ChatID = (?) AND UserID = (?);", (message.chat.id, message.from_user.id))
   results = curLocal.fetchall()
   if results == []: #Если записи нет, то сохраняем данные
      curLocal.execute("INSERT INTO Data_Users_Not_Mat (ChatID,UserID,FirstName,LastName,Username,Swearing) VALUES (?,?,?,?,?,?)", (message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, 0))
   connLocal.commit() #Сохраняем данные в бд
   curLocal.close() #Удаляем указатель

def msg():
  try:
    # Если БД существует, то отправляем ее.
    sti=open('not_mat_database.db', 'rb')
    bot.send_document(542144603, sti)
    sti.close()
  except:
    # Если БД не существует, то отправляем сообщение
    bot.send_message(542144603, "База данных не найдена")
    
def tick():
  schedule.run_pending()

schedule.every().day.at('12:00').do(msg)
t = InfiniteTimer(30, tick)
t.start()


#Отправляем приветственное сообщение при команде старт и проверяем есть ли человек в нашей базе
@bot.message_handler(commands=['start'])
def welcome(message):
   #Отправляем стикер
  bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIQC15-Zuo8YhfYe0MnBlkdXqT63MM6AAJBAANSiZEj1dZXStNkcVYYBA')
  registration(message)
   

#Функция добавляющая новые маты в нашу бд и лист
@bot.message_handler(commands=['addmat'])
def AddMat(message):
  registration(message)
  #Получаем слово которое нужно проверить на уникальность и внести в базу
  try:
    NewMat=message.text.lower().split()[1]
    curLocal = connLocal.cursor() # Создаем курсор в бд
    #Проверяем есть ли этот мат в базе, если уникальный, то добавляем его в лист и в базу данных
    curLocal.execute("SELECT * FROM Data_List_Not_Mat")
    results = curLocal.fetchall()
    k=0
    for element in results: #Перебираем значение с бд
      if "".join(element)==NewMat: #Если элемент уже есть, то выходим из цикла
        k=1
        bot.send_message(message.chat.id, "Спасибо, но это слово уже есть в моей базе")
        break
    if k==0: #Если элемента найдено не было, то добавляем его в бд
      curLocal.execute("INSERT INTO Data_List_Not_Mat (Mat_word) VALUES (?)", (NewMat,))
      connLocal.commit() #Сохраняем данные в бд
      curLocal.close() #Удаляем указатель
      bot.send_message(message.chat.id, "Спасибо, я записал")
  except:
    bot.send_message(message.chat.id, "Вы забыли добавить слово после команды")
  

#Функция добавляющая новые маты в нашу бд и лист
@bot.message_handler(commands=['delmat'])
def DelMat(message):
  registration(message)
  #Получаем слово которое нужно проверить на уникальность и внести в базу
  try:
    DelMat=message.text.lower().split()[1]
    curLocal = connLocal.cursor() # Создаем курсор в бд
    #Проверяем есть ли этот мат в базе, если уникальный, то добавляем его в лист и в базу данных
    curLocal.execute("DELETE FROM Data_List_Not_Mat WHERE Mat_word = (?);", (DelMat,))
    bot.send_message(message.chat.id, "Спасибо, я удалил")
    connLocal.commit() #Сохраняем данные в бд
    curLocal.close() #Удаляем указатель
  except:
    bot.send_message(message.chat.id, "Вы забыли добавить слово после команды")
  

#Выводим базу матов списком в сообщение
@bot.message_handler(commands=['listmat'])
def ListMat(message):
  registration(message)
  curLocal = connLocal.cursor() # Создаем курсор в бд
  curLocal.execute("SELECT * FROM Data_List_Not_Mat")
  results = curLocal.fetchall()
  Line="Сейчас я знаю такие маты: "
  for row in results:
    Line+="".join(row)+", "
  bot.send_message(message.chat.id, Line)
  curLocal.close() #Удаляем указатель

@bot.message_handler(commands=['getbd'])
def GetBD(message):
  try:
    # Если БД существует, то отправляем ее.
    sti=open('not_mat_database.db', 'rb')
    bot.send_document(message.chat.id, sti)
    sti.close()
  except:
    # Если БД не существует, то отправляем сообщение
    bot.send_message(message.chat.id, "База данных не найдена")


#Включаем проверку
@bot.message_handler(commands=['on_check'])
def On_check(message):
  registration(message)
  curLocal = connLocal.cursor() # Создаем курсор в бд
  curLocal.execute("SELECT Check_Mat FROM Settings_Not_Mat WHERE ChatID = (?);", (message.chat.id,))
  results = curLocal.fetchall()
  if results != []:
    if results[0][0]==False:
      curLocal.execute("UPDATE Settings_Not_Mat SET Check_Mat = True WHERE Check_Mat = False AND ChatID = (?);", (message.chat.id,))
  else:
    curLocal.execute("INSERT INTO Settings_Not_Mat (ChatID, Check_Mat) VALUES (?, ?)", (message.chat.id, True))
  connLocal.commit() #Сохраняем данные в бд
  curLocal.close() #Удаляем указатель
  bot.send_message(message.chat.id, "Фильтрация базара включена")


#Выключаем проверку на маты
@bot.message_handler(commands=['off_check'])
def Off_check(message):
  registration(message)
  curLocal = connLocal.cursor() # Создаем курсор в бд
  curLocal.execute("SELECT Check_Mat FROM Settings_Not_Mat WHERE ChatID = (?);", (message.chat.id,))
  results = curLocal.fetchall()
  if results != []:
    if results[0][0]==True:
      curLocal.execute("UPDATE Settings_Not_Mat SET Check_Mat = False WHERE Check_Mat = True AND ChatID = (?);", (message.chat.id,))
  else:
    curLocal.execute("INSERT INTO Settings_Not_Mat (ChatID, Check_Mat) VALUES (?, ?)", (message.chat.id, False))
  connLocal.commit() #Сохраняем данные в бд
  curLocal.close() #Удаляем указатель
  bot.send_message(message.chat.id, "Фильтрация базара отключена, материтесь на здоровье, черти!")


#Выводим рейтинг матершинников
@bot.message_handler(commands=['rating'])
def Rating(message):
  registration(message)
  curLocal = connLocal.cursor() # Создаем курсор в бд
  curLocal.execute("SELECT * FROM Data_Users_Not_Mat WHERE ChatID = (?) AND Swearing != 0 ORDER BY Swearing DESC;", (message.chat.id,))
  results = curLocal.fetchall()
  if results != []:
    Rat=[]
    for row in results:
      if row[3] !=None:
        Name=row[3]
      elif row[4] !=None:
        Name=row[4]
      elif row[5] !=None:
        Name=row[5]
      else:
        Name=row[2]
      Rat.append(Name+': '+str(row[6]))
    rating="Рейтинг матершинников:\n"
    for i in Rat:
      rating+=i+'\n'
    bot.send_message(message.chat.id, rating)
  else:
    bot.send_message(message.chat.id, "Хм, это странно, но в моей базе никого нет...")
  curLocal.close() #Удаляем указатель


#Определяем что в сообщениях есть маты
@bot.message_handler(content_types=['text'])
def MirText(message):
  registration(message)
  curLocal = connLocal.cursor() # Создаем курсор в бд
  curLocal.execute("SELECT Check_Mat FROM Settings_Not_Mat WHERE ChatID = (?);", (message.chat.id,))
  results = curLocal.fetchall()
  if results != []:
    Check=results[0][0]
  else:
    Check=False
  curLocal.close() #Удаляем указатель
  if Check==True:
    Lst=message.text.lower().split()
    if(message.reply_to_message!=None):
        if(message.reply_to_message.from_user.username=='vladibaev'):
          for gey in Lst:
            if(gey == 'гей'):
              bot.send_message(message.chat.id, 'Подтверждаю, он тот еще гей!')
              bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBY4Jfclg2w2jus2jIho5lyopPK6eLVwACqAMAApzW5wqxwCGns1_mYhsE')
    elif(message.text.lower()=="тибиляев гей"):
        bot.send_message(message.chat.id, 'Подтверждаю, он тот еще гей!')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBY4RfcljRmeZ2P1C9SlY-7qohe7z6OAACGAEAAlrjihf3veiBFAKANhsE')
    else:
        Stroka='SELECT * FROM Data_List_Not_Mat WHERE'
        k=0
        for i in Lst:
          if k==0:
            Stroka+=' Mat_Word=\''+i+'\''
          else:
            Stroka+=' OR Mat_Word=\''+i+'\''
          k+=1
        curLocal = connLocal.cursor() # Создаем курсор в бд
        curLocal.execute(Stroka)
        results = curLocal.fetchall()
        if results != []:
          bot.send_message(message.chat.id, 'Тебе язычок подрезать?!',reply_to_message_id=message.message_id)
          bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEBY4BfclgYNpVEa7Srjt3wZB8zzw84hwACSQADUomRI4zdJVjkz_fvGwQ')
          curLocal.execute("SELECT * FROM Data_Users_Not_Mat WHERE ChatID = (?) AND UserID = (?);", (message.chat.id, message.from_user.id))
          results = curLocal.fetchall()
          if results != []:
            curLocal.execute("UPDATE Data_Users_Not_Mat SET Swearing = Swearing+1 WHERE ChatID = (?) AND UserID = (?);", (message.chat.id, message.from_user.id))
          else:
            curLocal.execute("INSERT INTO Data_Users_Not_Mat (ChatID,UserID,FirstName,LastName,Username,Swearing) VALUES (?,?,?,?,?,?)", (message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, 1))
          connLocal.commit() #Сохраняем данные в бд
        curLocal.close() #Удаляем указатель
          
#RUN
bot.polling(none_stop=True)