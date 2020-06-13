import telebot
import psycopg2
import User
import Employee
from telebot import types
from datetime import datetime

from Controller import Controller

controller = Controller("d6ib69jeupvh36", "szvriplnadxleq",
                        "3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a",
                        "ec2-34-197-188-147.compute-1.amazonaws.com")

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')

astate = ""
user =User.User(0)

@bot.callback_query_handler(lambda query: query.data == "register")
def register2(query):
    user.change_state()
    print("Hello")
    print(user.get_state())
    global astate
    astate = 1




@bot.message_handler(commands=['start'])
def start_message(message):
    users = controller.user_exists(message.from_user.id)
    if len(users) == 0:
        keyboard = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(text="Yes", callback_data="register")

        keyboard.add(yes_button)

        bot.send_message(message.chat.id,
                         'Hello, it seems you are not registered.\nDo you want to register?',
                         reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id,
                         'Hello, ' + users[0][1])


@bot.message_handler(func=lambda message : user.get_state())
def user_entering_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    bot.send_message(message.chat.id, "Отличное имя, запомню! Теперь укажи, пожалуйста, свой возраст.")
    user.change_state()
    print(user.get_name())
    global astate
    astate = 0


@bot.message_handler(content_types=['text'])
def send_text(message):

    if message.text.lower() == 'привіт':
            bot.send_message(message.chat.id, 'Категорично вас вітаю пане, ' + message.from_user.first_name)
    elif message.text.lower() == 'бувай':
            bot.send_message(message.chat.id, 'Допобачення')
    elif message.text.lower() == 'де я?':
            bot.send_message(message.chat.id, 'Ось ти де')
            bot.send_location(message.chat.id, 49.33273504, 17.61087799)


bot.polling(none_stop=True, interval=0)

# controller.close()

# authorization = 0
# name = ''
# surname = ''
#
# conn = psycopg2.connect(dbname='d6ib69jeupvh36', user='szvriplnadxleq',
#                         password='3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a',
#                         host='ec2-34-197-188-147.compute-1.amazonaws.com')
# cursor = conn.cursor()
# cursor.execute('SELECT * FROM users')
# records = cursor.fetchall()
# print(records[1][1])
# for i in range(len(records)):
#     print(records[i][1])
# print(records)
# cursor.close()
# conn.close()
#
# bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')
# keyboard1 = telebot.types.ReplyKeyboardMarkup()
# keyboard1.row('Привіт', 'Бувай')
# keyboard1.row('Де я?')
# keyboard1.row('/authorization', '/users', '/geo_position')
#
#
# @bot.message_handler(commands=['start'])
# def start_message(message):
#     bot.send_message(message.chat.id,
#                      'Hi, it is a really beginning of our messaging',
#                      reply_markup=keyboard1)
#
#
# @bot.message_handler(commands=['authorization'])
# def authorization(message):
#     bot.send_message(message.chat.id, 'Авторизація. Напиши мені своє ім\'я', reply_markup=keyboard1)
#     global authorization
#     authorization = 1
#
#
# @bot.message_handler(commands=['users'])
# def users(message):
#     cursor.execute('SELECT * FROM users')
#     records = cursor.fetchall()
#
#     for i in range(len(records)):
#         bot.send_message(message.chat.id,
#                          '%s користувач: %s, %s, %s' % (i + 1, records[i][1], records[i][2], records[i][0]),
#                          reply_markup=keyboard1)
#
# @bot.message_handler(commands=['help'])
# def help(message):
#     bot.send_message(message.chat.id, 'Пиши /start і починай роботу!', reply_markup=keyboard1)
#
#
# @bot.message_handler(commands=["geo_position"])
# def geo_position(message):
#     # Эти параметры для клавиатуры необязательны, просто для удобства
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     button_phone = types.KeyboardButton(text="Відправити номер телефона", request_contact=True)
#     button_geo = types.KeyboardButton(text="Відправити геолокацію", request_location=True)
#     keyboard.add(button_phone, button_geo)
#     bot.send_message(message.chat.id, "Ти можеш відправити мені свій номер телефона або геолокацію!",
#                      reply_markup=keyboard)
#
#
# @bot.message_handler(content_types=['text'])
# def send_text(message):
#     global authorization
#
#     if authorization == 1:
#         bot.send_message(message.chat.id, 'Добре , тепер напиши мені своє прізвище) ')
#         global name
#         name = message.text
#         authorization = 2
#     elif authorization == 2:
#         bot.send_message(message.chat.id, 'Тебе успішно авторизовано!) ')
#         global surname
#         surname = message.text
#         user = User.User(name, surname, message.from_user.id)
#         user.add()
#         authorization = 0
#     else:
#         if message.text.lower() == 'привіт':
#             bot.send_message(message.chat.id, 'Категорично вас вітаю пане, ' + message.from_user.first_name)
#         elif message.text.lower() == 'бувай':
#             bot.send_message(message.chat.id, 'Допобачення')
#         elif message.text.lower() == 'де я?':
#             bot.send_message(message.chat.id, 'Ось ти де')
#             bot.send_location(message.chat.id, 49.33273504, 17.61087799)
#
#
# @bot.message_handler(content_types=['sticker'])
# def sticker_id(message):
#     print(message)
#
# bot.polling(none_stop=True, interval=0)
