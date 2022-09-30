# Импортируем модули
import telebot
import config as cfg
import sqlite3
import random as rand

# Все настройки в config.py
# Автор данного кода: 0xSn1kky

# Подключение к боту
bot = telebot.TeleBot(cfg.token, parse_mode = None)
# Подключение базы данных
db = sqlite3.connect('data.db', check_same_thread=False )
cursor = db.cursor()
# Создание Базы Данных
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER,
    balance INTEGER
)""")
db.commit()

# Команда /start
@bot.message_handler(commands=['start'])
def start (message):
    usrid = message.chat.id
    # Проверяем есть ли пользователь в системе
    cursor.execute(f"SELECT id FROM users WHERE id = {usrid}")
    info = cursor.fetchone()
    # Проверка на существование пользователя
    if info is None:
        # Добавляем подьзователя в бд
        cursor.execute("INSERT INTO users VALUES (?, ?)", (usrid, cfg.bmoney))
        # Отправляем приветсвтенное сообщение
        bot.send_message(message.chat.id, f"Привет 👋 я {cfg.botname} тут ты сможешь поиграть в казино. Ты был успешно зарегестрирован! Ладно держи {cfg.bmoney}$ играй сколько хочешь! Если что /help - список команд")
        db.commit()
        print("LOG SYSTEM>>> New User")    
    else:
        # сообщения при ошибке 
        bot.send_message(message.chat.id, "Ты уже зарегестрирован!")
  
# Команда /balance
@bot.message_handler(commands=['balance'])
def balance (message):
    userid = message.chat.id
    # Узанем баланс пользователя
    cursor.execute(f"SELECT balance FROM users WHERE id = {userid}")
    b = cursor.fetchone()
    balance = b[0]
    
    bot.reply_to(message, f"Баланс: {balance}$")
  
# Команда /help
@bot.message_handler(commands=['help'])
def help (message):
    bot.send_message(message.chat.id, "📁┇ Список команд:\n /bonus - получить 5000$ (Только если баланс равен 0)\n /balance - посмотреть баланс\n /casino - Играть в казино")
 
# Команда /bonus  
@bot.message_handler(commands=['bonus'])
def bonus (message):
    # Проверка баланса
    usrid = message.chat.id
    b = cursor.execute(f"SELECT balance FROM users WHERE id = {usrid}").fetchone()
    balance = b[0]
    if balance < 1:
        # Выдача денег
        bot.send_message(message.chat.id, "Держи бонус! 5000")
        cursor.execute(f"UPDATE users SET balance = 5000 WHERE id = {usrid}")
        db.commit()
        # сообщение при ошибке
    else:
        bot.send_message(message.chat.id, "У вас денег больше чем 0")

# Узнать chat.id        
@bot.message_handler(commands=['userid'])
def userid (message):
    bot.send_message(message.chat.id, message.chat.id)
# Установка денег
@bot.message_handler(commands=['setmoney'])
def admin (message):
    if message.chat.id == cfg.ownerid:
       msg = bot.send_message(message.chat.id, "Введите сумму которую хотите установить себе на баланс")
       bot.register_next_step_handler(msg, summa)
    else:
        bot.send_message(message.chat.id, "У вас нет прав!")
def summa (message):
    txt = message.text
    usrid = message.chat.id
    cursor.execute(f"UPDATE users SET balance = {txt} WHERE id = {usrid}")
    db.commit()    
    
@bot.message_handler(commands=['stop'])
def stp (message):
    if message.chat.id == cfg.ownerid:
        bot.send_message(message.chat.id, "Бот остановлен")
        db.close()
        exit(0)
 
# Казино 
@bot.message_handler(commands=['casino'])
def casino (message):
    msg = bot.send_message(message.chat.id, "Пожалуйста введите сумму ставки")
    bot.register_next_step_handler(msg, casinoplay)
def casinoplay (message):
    usrid = message.chat.id
    try:
        st = message.text
        stavka = int(st)
        b = cursor.execute(f"SELECT balance FROM users WHERE id = {usrid}").fetchone()
        ba= b[0]
        if ba >= stavka:
            bot.send_message(message.chat.id, f"Вы указали ставку {stavka}$ игра начинается!")
            rnd = rand.randint(1, 3)
            if rnd == 1:
                print("LOG SYSTEM>>> User Lost")
                y = stavka
                bot.send_message(message.chat.id, "Очень жаль, но вы проиграли ❌ ")
                cursor.execute(f'UPDATE users SET balance = balance - {y} WHERE id = {message.chat.id}')
            if rnd == 2:
                print("LOG SYSTEM>>> User did not win or lose")
                bot.send_message(message.chat.id, "😕 Вы не проиграли, но и не выйграли")
            if rnd == 3:
                print("LOG SYSTEM>>> User Win")
                y = stavka
                bot.send_message(message.chat.id, "🎉 Поздравляем вы выйграли!")
                cursor.execute(f'UPDATE users SET balance = balance + {y} WHERE id = {message.chat.id}')
			    
        else:
            bot.send_message(message.chat.id, "У вас недостаточно денег чтобы сыграть на такую ставку!")
    except:
        bot.send_message(message.chat.id, "Это не число!")
    db.commit()
 
bot.polling(none_stop=True, interval=0)