import telebot
import psycopg2
import User
import Employee
from telebot import types
from datetime import datetime
from pprint import pprint

from Controller import Controller

controller = Controller("d6ib69jeupvh36", "szvriplnadxleq",
                        "3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a",
                        "ec2-34-197-188-147.compute-1.amazonaws.com")

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')

state = ""
state = 0
current_user = User.User()


@bot.callback_query_handler(lambda query: query.data == "register")
def register(query):
    global state
    state = 1
    current_user.identifier = query.message.from_user.id
    bot.send_message(query.message.chat.id, "Enter your name")


@bot.message_handler(func=lambda message: state == 1)
def user_name(message):
    global state
    state = 2
    current_user.name = message.text
    bot.send_message(message.chat.id, "Enter your surname")


@bot.message_handler(func=lambda message: state == 2)
def user_surname(message):
    global state
    state = 3
    current_user.surname = message.text
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    send_button = types.KeyboardButton(text="Send", request_contact=True)
    keyboard.add(send_button)
    bot.send_message(message.chat.id, "Send your phone number", reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def get_contact(message):
    bot.send_message(message.chat.id, 'О класс спасибо за контакт')
    print(message.contact.phone_number)
    current_user.number = message.contact.phone_number


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


bot.polling(none_stop=True, interval=0)