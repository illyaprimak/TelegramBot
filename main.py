import telebot
import psycopg2
import Customer
from telebot import types

autorization = 0
name = ''
surname = ''

conn = psycopg2.connect(dbname='dcur3f5qg9nbp9', user='tbhawhpdqppahx',
                        password='2a58a610fa0064b79d45735606512a9994a9c43a4b2ba30dc3467ae3c375af26',
                        host='ec2-18-232-143-90.compute-1.amazonaws.com')
cursor = conn.cursor()
cursor.execute('SELECT * FROM users')
records = cursor.fetchall()
print(records[1][1])
for i in range(len(records)):
    print(records[i][1])
print(records)
cursor.close()
conn.close()

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Привіт', 'Бувай')
keyboard1.row('Де я?')
keyboard1.row('/autorization')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Доброго дня, козаче! Я бот що здає в аренду електросамокати та велосипеди. Якщо хочешь щось від мене, то натискай на кнопки))0)0)', reply_markup=keyboard1)

@bot.message_handler(commands=['autorization'])
def start_message(message):
    bot.send_message(message.chat.id, 'Авторизація. Напиши мені своє ім\'я', reply_markup=keyboard1)
    global autorization
    autorization = 1

@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Пиши /start і починай роботу!', reply_markup=keyboard1)


@bot.message_handler(commands=["geophone"])
def geophone(message):
    # Эти параметры для клавиатуры необязательны, просто для удобства
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Відправити номер телефона", request_contact=True)
    button_geo = types.KeyboardButton(text="Відправити геолокацію", request_location=True)
    keyboard.add(button_phone, button_geo)
    bot.send_message(message.chat.id, "Ти можеш відправити мені свій номер телефона або геолокацію!", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global autorization

    if(autorization == 1):
        bot.send_message(message.chat.id,'Добре , тепер напиши мені своє прізвище) ')
        global name
        name = message.text
        autorization = 2
    elif(autorization == 2):
        bot.send_message(message.chat.id, 'Тебе успішно авторизовано!) ')
        global surname
        surname = message.text
        user = Customer.User(name,surname,message.from_user.id)
        user.add()
        autorization = 0
    else:
        if message.text.lower() == 'привіт':
            bot.send_message(message.chat.id, 'Категорично вас вітаю пане, ' + message.from_user.first_name)
        elif message.text.lower() == 'бувай':
            bot.send_message(message.chat.id, 'Допобачення')
        elif message.text.lower() == 'де я?':
            bot.send_message(message.chat.id, 'Ось ти де')
            bot.send_location(message.chat.id, 49.33273504 , 17.61087799)

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)

bot.polling(none_stop=True, interval=0)