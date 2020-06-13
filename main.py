import telebot
import datetime
import geopy
import telebot_calendar
import psycopg2
import User
import Employee
from telebot import types
from pprint import pprint
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from geopy.geocoders import Nominatim
from datetime import datetime
from Controller import Controller

controller = Controller("d6ib69jeupvh36", "szvriplnadxleq",
                        "3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a",
                        "ec2-34-197-188-147.compute-1.amazonaws.com")

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')

current_user = User.User()


@bot.message_handler(commands=['start'])
def start_message(message):
    users = controller.user_exists(message.from_user.id)
    if len(users) == 0:
        global current_user
        current_user = User.User()
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Register", callback_data="register")
        )
        bot.send_message(message.chat.id,
                         'Hello, it seems you are not registered.\nDo you want to register?',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         'Hello, ' + users[0][1])


@bot.callback_query_handler(func=lambda call: call.data.startswith("register"))
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    current_user.identifier = call.message.from_user.id
    current_user.bonus_points = 0

    message = bot.send_message(call.message.chat.id, "Enter your name", reply_markup=None)

    bot.register_next_step_handler(message, user_name)


@bot.message_handler(content_types=['text'])
def default(message):
    bot.send_message(message.chat.id, "Unknown command")


def user_name(message):
    current_user.name = message.text

    message = bot.send_message(message.chat.id, "Enter your surname")

    bot.register_next_step_handler(message, user_surname)


def user_surname(message):
    current_user.surname = message.text

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    send_button = types.KeyboardButton(text="Send", request_contact=True)
    keyboard.add(send_button)

    message = bot.send_message(message.chat.id, "Send your phone number", reply_markup=keyboard)

    bot.register_next_step_handler(message, user_contact)


@bot.message_handler(content_types=['contact'])
def user_contact(message):
    current_user.number = message.contact.phone_number

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    send_button = types.KeyboardButton(text="Send", request_location=True)
    keyboard.add(send_button)
    message = bot.send_message(message.chat.id, 'Send your location',
                               reply_markup=keyboard)

    bot.register_next_step_handler(message, user_location)


@bot.message_handler(content_types=['location'])
def user_location(message):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.reverse(str(message.location.latitude) + ", " + str(message.location.longitude))
    current_user.country = location.raw['address']['country']
    current_user.city = location.raw['address']['city']

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
    )
    bot.send_message(
        message.chat.id, "Choose your birthday date", reply_markup=keyboard
    )


calendar = CallbackData("calendar_1", "action", "year", "month", "day")


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def callback_inline(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar.sep)
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        message = bot.send_message(call.message.chat.id, "You are successfully registered")
        bot.register_next_step_handler(message, default)
        current_user.birth_date = date
    elif action == "CANCEL":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
        )
        bot.send_message(
            call.from_user.id, "Please choose your birthday date", reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("getdate"))
def callback_inline(call: CallbackQuery):
    if call.data == "getdate":
        now = datetime.now()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Selected date",
            reply_markup=telebot_calendar.create_calendar(
                name=calendar.prefix,
                year=now.year,
                month=now.month,
            ),
        )


bot.polling(none_stop=True, interval=0)
