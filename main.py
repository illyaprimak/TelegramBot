import telebot
import re
import datetime
from datetime import timedelta
import geopy
from geopy.distance import geodesic
import Controller
import Vehicle
import Zone
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
current_employee = Employee.Employee()
all_scooters = []

for vehicle in controller.get_all("vehicle"):
    all_scooters.append(
        Vehicle.Vehicle(vehicle[0], vehicle[1], vehicle[2], vehicle[3], vehicle[4], vehicle[5], vehicle[6], vehicle[7],
                        vehicle[8]))


def insert_user():
    controller.insert(current_user)
    for card in current_user.cards:
        controller.insert(card)


def rent_handler(vehicle_identifier):
    current_vehicle = controller.get_vehicle(vehicle_identifier)[0]
    current_vehicle = Vehicle.Vehicle(current_vehicle[0], current_vehicle[1], current_vehicle[2], current_vehicle[3],
                                      current_vehicle[4], current_vehicle[5], current_vehicle[6], current_vehicle[7],
                                      current_vehicle[8])
    controller.add_ride(current_user, current_vehicle)
    current_user.currently_used_vehicle = current_vehicle


def end_ride_handler(latitude, longitude):
    controller.end_vehicle_rent(current_user.currently_used_vehicle, latitude, longitude)
    controller.end_ride(datetime.now(), current_user, current_user.currently_used_vehicle)


@bot.message_handler(commands=['start'])
def start_message(message):
    user = controller.user_exists(message.from_user.id)
    employee = controller.employee_exists(message.from_user.id)
    persons = user + employee
    if len(persons) == 0:
        global current_user
        current_user = User.User()
        global current_employee
        current_employee = Employee.Employee()
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Like user 🔑", callback_data="register"),
            telebot.types.InlineKeyboardButton("Like employee 🛠️", callback_data="register_emp")
        )
        bot.send_message(message.chat.id,
                         '👋 Hello, it seems you are not registered.\nDo you want to register?',
                         reply_markup=keyboard)
    else:
        user = user[0]
        current_user = User.User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])
        for card in controller.get_cards(current_user):
            current_user.cards.append(Card.Card(card[1], card[2]))
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("See nearest scooters 🛴", callback_data="nearest_scooters"))
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("Start a ride 🛴", callback_data="rent_scooter"))

        bot.send_message(message.chat.id, '👋 Hello, ' + current_user.name, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "nearest_scooters")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=bool(True))
    keyboard.add(types.KeyboardButton(text="Send 📍", request_location=True))
    message = bot.send_message(call.message.chat.id,
                               'First, provide your location so we could find nearest variants for you 📍',
                               reply_markup=keyboard)
    bot.register_next_step_handler(message, current_user_location)


@bot.callback_query_handler(func=lambda call: call.data == "rent_scooter")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id,
                               "Enter the scooter's unique code")
    bot.register_next_step_handler(message, rent_by_id)


@bot.callback_query_handler(func=lambda call: call.data == "end_ride")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=bool(True))
    keyboard.add(types.KeyboardButton(text="Send 📍", request_location=True))
    message = bot.send_message(call.message.chat.id, text="Send your location", reply_markup=keyboard)
    bot.register_next_step_handler(message, current_user_location_ride_end)


@bot.callback_query_handler(func=lambda call: call.data.startswith("send_scooter_location"))
def send_scooter_location(call):
    bot.answer_callback_query(call.id)
    latitude = float(call.data.split('|')[1])
    longitude = float(call.data.split('|')[2])
    bot.send_message(call.message.chat.id, "Chosen scooter's coordinates 📍\nCode to ride: " + call.data.split('|')[3],
                     reply_markup=ReplyKeyboardRemove())
    bot.send_location(
        chat_id=call.message.chat.id,
        latitude=latitude,
        longitude=longitude
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("end_rent"))
def send_scooter_location(call):
    bot.answer_callback_query(call.id)
    latitude = float(call.data.split('|')[1])
    longitude = float(call.data.split('|')[2])
    end_ride_handler(latitude, longitude)
    bot.send_message(call.message.chat.id, "Ride ended", reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda call: call.data == "register")
def register(call):
    current_user.identifier = call.from_user.id
    current_user.cards = []
    current_user.bonus_points = 0

    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    message = bot.send_message(call.message.chat.id, "Enter your name ✏")
    bot.register_next_step_handler(message, user_name)


@bot.callback_query_handler(func=lambda call: call.data == "register_emp")
def register(call):
    current_employee.identifier = call.from_user.id
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("Charger ⚡", callback_data="charger"),
        telebot.types.InlineKeyboardButton("Repairer 🛠️", callback_data="repairer")
    )

    bot.send_message(call.message.chat.id, "Register as charger or repairer", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "charger")
def register(call):
    current_employee.specialization = False
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    controller.insert(current_employee)
    bot.send_message(call.message.chat.id, "You are registered as charger ⚡")


@bot.callback_query_handler(func=lambda call: call.data == "repairer")
def register(call):
    current_employee.specialization = True
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    controller.insert(current_employee)
    bot.send_message(call.message.chat.id, "You are registered as repairer 🛠️")


@bot.message_handler()
def default(message):
    if len(controller.user_exists(message.from_user.id)) > 0:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("See nearest scooters 🛴", callback_data="nearest_scooters"),
            telebot.types.InlineKeyboardButton("Rent scooter by id 🛴", callback_data="rent_scooter")
        )
        bot.send_message(message.chat.id, text="Please use the menu 📋", reply_markup=keyboard)
    elif len(controller.employee_exists(message.from_user.id)) > 0:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Charge ⚡", callback_data=""),
            telebot.types.InlineKeyboardButton("Repair 🛠️", callback_data="")
        )
        bot.send_message(message.chat.id, text="Please use the menu 📋", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Please use the menu 📋")


@bot.message_handler(content_types=['text'])
def user_name(message):
    if message.text is None:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, user_name)
    else:
        current_user.name = message.text
        message = bot.send_message(message.chat.id, "Enter your surname ✏")
        bot.register_next_step_handler(message, user_surname)


def rent_by_id(message):
    if message.text is None:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, rent_by_id)
    elif message.text.isdigit():
        rent_handler(message.text)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton("End ride 🛑", callback_data="end_ride"))
        bot.send_message(message.chat.id, "Use the button below to end ride ⬇️", reply_markup=keyboard)


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
            message = bot.send_message(message.chat.id, "Registration finished ✅")
            insert_user()
            bot.register_for_reply(message, default)
    elif len(message.text) > 15:
        bot.send_message(message.chat.id, "Card name is too long, try again ❌")
        bot.register_next_step_handler(message, user_card)


@bot.callback_query_handler(func=lambda call: call.data == "add_card")
def add_card(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, "Specify the card name 💳")
    bot.register_next_step_handler(message, user_card)


@bot.callback_query_handler(func=lambda call: call.data == "stop_adding_cards")
def stop_adding_cards(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, "Registration finished ✅")
    insert_user()
    bot.register_for_reply(message, default)


@bot.message_handler(content_types=['contact', 'text'])
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
def current_user_location(message):
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude
        keyboard = telebot.types.InlineKeyboardMarkup()
        scooters = []

        def get_first(elem):
            return elem[0]

        for scooter in all_scooters:
            scooters.append([round(geodesic((latitude, longitude), (scooter.latitude, scooter.longitude)).meters),
                             scooter])
        scooters.sort(key=get_first)

        del scooters[3:]

        for scooter in scooters:
            scooter = scooter[1]
            keyboard.row().add(
                telebot.types.InlineKeyboardButton(
                    "🛴 🗺️ " + str(
                        round(geodesic((latitude, longitude), (scooter.latitude, scooter.longitude)).meters)) +
                    "m 🔋 " + str(scooter.charge_level) + "% "
                    + str(scooter.cents_per_minute) + "¢/min",
                    callback_data="send_scooter_location|" + str(scooter.latitude) + "|" + str(
                        scooter.longitude) + "|" + str(scooter.identifier)))
        bot.send_message(message.chat.id, "Nearest scooters", reply_markup=keyboard)
    except AttributeError:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, current_user_location)


def current_user_location_ride_end(message):
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude
        keyboard = telebot.types.InlineKeyboardMarkup()
        for card in current_user.cards:
            keyboard.row().add(
                telebot.types.InlineKeyboardButton(card.name,
                                                   callback_data="end_rent|" + str(latitude) + "|" + str(longitude)))
        message = bot.send_message(message.chat.id, "Choose card to pay", reply_markup=keyboard)
        bot.register_next_step_handler(message, default)
    except AttributeError:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, current_user_location_ride_end)


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
        adult = timedelta(days=6575)
        if (datetime.now() - adult) > date:
            current_user.birth_date = date

            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=bool(True))
            keyboard.add(types.KeyboardButton(text="Send ☎", request_contact=True))
            message = bot.send_message(call.message.chat.id, "Send your phone number ☎", reply_markup=keyboard)
            bot.register_next_step_handler(message, user_contact)
        else:
            bot.send_message(call.from_user.id, "You are under eighteen, try again")
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
            )
            bot.send_message(call.from_user.id, "Choose your birthday date 📅", reply_markup=keyboard)
    elif action == "CANCEL":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Choose", callback_data="getdate")
        )
        bot.send_message(
            call.from_user.id, "Please choose your birthday date 📅", reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: call.data == "getdate")
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
