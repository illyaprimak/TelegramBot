import telebot
import re
import datetime
import geopy
import telebot_calendar
import psycopg2
import User
import Card
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


def registration_handler():
    controller.insert(current_user)
    for card in current_user.cards:
        controller.insert(card)


@bot.message_handler(commands=['start'])
def start_message(message):
    users = controller.user_exists(message.from_user.id)
    if len(users) == 0:
        global current_user
        current_user = User.User()
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Register 🔑", callback_data="register")
        )
        bot.send_message(message.chat.id,
                         '👋 Hello, it seems you are not registered.\nDo you want to register?',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         '👋 Hello, ' + users[0][1])


@bot.callback_query_handler(func=lambda call: call.data.startswith("register"))
def register(call):
    current_user.identifier = call.message.from_user.id
    current_user.cards = []
    current_user.bonus_points = 0

    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    message = bot.send_message(call.message.chat.id, "Enter your name ✏")
    bot.register_next_step_handler(message, user_name)


@bot.message_handler(content_types=['text'])
def default(message):
    bot.send_message(message.chat.id, "Please use the menu 📋")


def user_name(message):
    if message.text is None:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, user_name)
    else:
        current_user.name = message.text
        message = bot.send_message(message.chat.id, "Enter your surname ✏")
        bot.register_next_step_handler(message, user_surname)


def user_surname(message):
    if message.text is None:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, user_surname)
    else:
        current_user.surname = message.text
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
        )
        bot.send_message(message.chat.id, "Choose your birthday date 📅", reply_markup=keyboard)


def user_card(message):
    pprint(vars(current_user))
    if message.text is None:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, user_card)
    elif len(message.text) <= 15:
        current_user.cards.append(Card.Card(message.text, current_user.identifier))
        if len(current_user.cards) < 3:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton("Yes", callback_data="add_card"),
                telebot.types.InlineKeyboardButton("No", callback_data="stop_adding_cards")
            )
            bot.send_message(message.chat.id, "Add another one?", reply_markup=keyboard)
        else:
            message = bot.send_message(message.chat.id, "Maximal number of cards added, registration finished ✅")
            registration_handler()
            bot.register_next_step_handler(message, default)
    elif len(message.text) > 15:
        bot.send_message(message.chat.id, "Card name is too long, try again ❌")
        bot.register_next_step_handler(message, user_card)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_card"))
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, "Specify the card name 💳")
    bot.register_next_step_handler(message, user_card)


@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_adding_cards"))
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, "Cards added, registration finished ✅")
    registration_handler()
    bot.register_next_step_handler(message, default)


@bot.message_handler(content_types=['contact', 'text'])
def default(message):
    bot.send_message(message.chat.id, "Please use the menu 📋")


def user_contact(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Send 📍", request_location=True))
    try:
        current_user.number = message.contact.phone_number
        message = bot.send_message(message.chat.id, 'Send your location 📍',
                                   reply_markup=keyboard)
        bot.register_next_step_handler(message, user_location)
    except AttributeError:
        try:
            if re.compile("\+\d{12}|\d{12}|\d{10}").fullmatch(message.text):
                message = bot.send_message(message.chat.id, 'Send your location 📍',
                                           reply_markup=keyboard)
                current_user.number = message.text
                bot.register_next_step_handler(message, user_location)
            else:
                bot.send_message(message.chat.id, "Wrong pattern, try again ❌")
                bot.register_next_step_handler(message, user_contact)
        except AttributeError:
            bot.send_message(message.chat.id, "Wrong input, try again ❌")
            bot.register_next_step_handler(message, user_contact)


@bot.message_handler(content_types=['location'])
def default(message):
    bot.send_message(message.chat.id, "Please use the menu 📋")


def user_location(message):
    try:
        locator = Nominatim(user_agent="myGeocoder")
        location = locator.reverse(str(message.location.latitude) + ", " + str(message.location.longitude))
        try:
            current_user.country = location.raw['address']['country']
            current_user.city = location.raw['address']['city']
            bot.send_message(
                message.chat.id,
                "Your country: " + current_user.country + "\nYour city: " + current_user.city + "\n\n" +
                "Now, specify at least one card name 💳",
                reply_markup=ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, user_card)
        except KeyError:
            try:
                current_user.country = location.raw['address']['country']
                current_user.city = location.raw['address']['village']
                bot.send_message(
                    message.chat.id,
                    "Your country: " + current_user.country + "\nYour city: " + current_user.city + "\n\n" +
                    "Now, specify at least one card name 💳",
                    reply_markup=ReplyKeyboardRemove()
                )
                bot.register_next_step_handler(message, user_card)
            except KeyError:
                try:
                    pprint(vars(current_user))
                    bot.send_message(
                        message.chat.id,
                        "Your country: " + str(current_user.country) + "\nYour city: " + str(
                            current_user.city) + "\n\n" +
                        "Now, specify at least one card name 💳",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    bot.register_next_step_handler(message, user_card)
                except KeyError:
                    bot.send_message(message.chat.id, "Couldn't find your location, try again ❌")
                    bot.register_next_step_handler(message, user_location)
    except AttributeError:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, user_location)


calendar = CallbackData("calendar", "action", "year", "month", "day")


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar.prefix))
def callback_inline(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar.sep)
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        current_user.birth_date = date

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=bool(True))
        keyboard.add(types.KeyboardButton(text="Send ☎", request_contact=True))
        message = bot.send_message(call.message.chat.id, "Send your phone number ☎", reply_markup=keyboard)
        bot.register_next_step_handler(message, user_contact)

    elif action == "CANCEL":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
        )
        bot.send_message(
            call.from_user.id, "Please choose your birthday date 📅", reply_markup=keyboard
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
