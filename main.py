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
import Serve
from telebot import types
from pprint import pprint
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from geopy.geocoders import Nominatim
from Controller import Controller
from datetime import datetime

controller = Controller("d6ib69jeupvh36", "szvriplnadxleq",
                        "3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a",
                        "ec2-34-197-188-147.compute-1.amazonaws.com")

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')

current_user = User.User()
current_employee = Employee.Employee()


def insert_user():
    controller.insert(current_user)
    for card in current_user.cards:
        controller.insert(card)


def rent_handler(vehicle_identifier):
    current_vehicle = controller.get_vehicle(vehicle_identifier)
    if len(current_vehicle) == 0:
        return 3
    current_vehicle = current_vehicle[0]
    current_vehicle = Vehicle.Vehicle(current_vehicle[0], current_vehicle[1], current_vehicle[2],
                                      current_vehicle[3], current_vehicle[4], current_vehicle[5],
                                      current_vehicle[6], current_vehicle[7], current_vehicle[8])
    if current_vehicle.taken is True:
        return 1
    elif current_vehicle.technical_state is False:
        return 2
    else:
        controller.add_ride(current_user, current_vehicle)
        current_user.currently_used_vehicle = current_vehicle
        return 0


def end_ride_handler(latitude, longitude, zone_id, payment):
    controller.end_vehicle_rent(current_user.currently_used_vehicle, latitude, longitude, zone_id)
    controller.end_ride(datetime.now(), current_user, current_user.currently_used_vehicle, payment)
    current_user.currently_used_vehicle = None


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
            telebot.types.InlineKeyboardButton("As user 🔑", callback_data="register"),
            telebot.types.InlineKeyboardButton("As employee 🛠️", callback_data="register_emp")
        )

        bot.send_message(message.chat.id,
                         '👋 Hello, it seems you are not registered.\nDo you want to register?',
                         reply_markup=keyboard)
    elif len(employee) == 0:
        user = user[0]
        if current_user.identifier is None:
            current_user = User.User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])
            current_user.cards = []
            for card in controller.get_cards(current_user):
                current_user.cards.append(Card.Card(card[1], card[2]))
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("Nearest scooters 🗺️", callback_data="nearest_scooters"))
        if current_user.currently_used_vehicle is None:
            keyboard.row().add(
                telebot.types.InlineKeyboardButton("Start a ride 🛴", callback_data="rent_scooter"))
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("All my rides 🗒️", callback_data="all_rides"))
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("Total spent 💵", callback_data="all_expenses"))
        bot.send_message(message.chat.id, '👋 Hello, ' + current_user.name, reply_markup=keyboard)
    else:
        employee = employee[0]
        current_employee = Employee.Employee(employee[0], employee[1])
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(

            telebot.types.InlineKeyboardButton("Statistic 📝",
                                               callback_data="statistic")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("See nearest scooters 🗺️", callback_data="nearest_scooters")

        )
        bot.send_message(message.chat.id, '👋 Hello, employee', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "statistic")
def statistic(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("1",
                                           callback_data="general")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("2",
                                           callback_data="broken")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("3",
                                           callback_data="area")
    )
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id,
                     "Choose statistic\n1.Get general statistic about your serves\n2.Get information about which was the last who ride on the broken bicicles\n3.Find employees who serve all vehicles in zones whose radius would be greater than the parameter",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "general")
def general(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    str1 = "General statistic:"
    if len(controller.get_statistic(call.from_user.id)) == 0:
        message = bot.send_message(call.message.chat.id, "There no vehicles that you serve")
    else:
        for row in controller.get_statistic(call.from_user.id):
            str1 = str1 + "\nVehicle number: " + str(row[0]) + ", amount of your serves: " + str(
                row[1]) + ", amount of all serves: " + str(row[2])
        message = bot.send_message(call.message.chat.id, str1)
    bot.register_next_step_handler(message, default)


@bot.callback_query_handler(func=lambda call: call.data == "broken")
def broken(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    str1 = "Users who broke scooters:"
    if len(controller.get_broken_users()) == 0:
       message = bot.send_message(call.message.chat.id, "There no such users")
    else:
        for row in controller.get_broken_users():
            str1 = str1 + "\nUser name: " + str(row[0]) + ", user id: " + str(row[1])
        message = bot.send_message(call.message.chat.id, str1)
    bot.register_next_step_handler(message, default)


@bot.callback_query_handler(func=lambda call: call.data == "area")
def area(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = bot.send_message(call.message.chat.id, "Enter radius of area")
    bot.register_next_step_handler(message, radius_handler)


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
    message = bot.send_message(call.message.chat.id, "Enter the scooter's unique code")
    bot.register_next_step_handler(message, rent_by_id)


@bot.callback_query_handler(func=lambda call: call.data == "all_expenses")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if len(controller.get_payments_sum(current_user)) > 0:
        bot.send_message(call.message.chat.id,
                         "You have spent " + controller.get_payments_sum(current_user)[0][1] + " in total 💵")
    else:
        bot.send_message(call.message.chat.id, "It seems you do not have completed rides yet")


@bot.callback_query_handler(func=lambda call: call.data == "all_rides")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    message = ''
    rides = controller.get_users_rides(current_user)
    if len(rides) != 0:
        for ride in rides:
            message += '👉 ' + ride[0].strftime("%m/%d/%Y") + " " + str(
                int((ride[1] - ride[0]).total_seconds() // 60)) + "m " + str(ride[2]) + "\n"
    else:
        message = "It seems you do not have completed rides yet"
    bot.send_message(call.message.chat.id, message)


@bot.callback_query_handler(func=lambda call: call.data == "end_ride")
def register(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=bool(True))
    keyboard.add(types.KeyboardButton(text="Send 📍", request_location=True))
    message = bot.send_message(call.message.chat.id, text="Send your location 📍", reply_markup=keyboard)
    bot.register_next_step_handler(message, current_user_location_ride_end)


@bot.callback_query_handler(func=lambda call: call.data.startswith("send_scooter_location"))
def send_scooter_location(call):
    bot.answer_callback_query(call.id)
    latitude = float(call.data.split('|')[1])
    longitude = float(call.data.split('|')[2])
    if len(controller.employee_exists(call.from_user.id)) != 0:
        spec = controller.get_specialization(call.from_user.id)[0][0]
        keyboard = telebot.types.InlineKeyboardMarkup()
        if spec is False:
            keyboard.row(
                telebot.types.InlineKeyboardButton("Charge ⚡",
                                                   callback_data="charge_vehicle|" + call.data.split('|')[3])
            )
        else:
            keyboard.row(
                telebot.types.InlineKeyboardButton("Repair 🛠️",
                                                   callback_data="repair_vehicle|" + call.data.split('|')[3])
            )
        bot.send_message(call.message.chat.id,
                         "Chosen scooter's coordinates 📍",
                         reply_markup=ReplyKeyboardRemove())
        bot.send_location(
            chat_id=call.message.chat.id,
            latitude=latitude,
            longitude=longitude,
            reply_markup=keyboard
        )
    else:
        bot.send_message(call.message.chat.id,
                         "Chosen scooter's coordinates 📍\nCode to ride: " + call.data.split('|')[3],
                         reply_markup=ReplyKeyboardRemove())
        bot.send_location(
            chat_id=call.message.chat.id,
            latitude=latitude,
            longitude=longitude
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("charge_vehicle"))
def charge(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    controller.insert(Serve.Serve(call.from_user.id, call.data.split('|')[1]))
    bot.send_message(call.message.chat.id,
                     "Great job! You charged scooter with id = " + call.data.split('|')[1],
                     reply_markup=ReplyKeyboardRemove())
    controller.serve_vehicle(call.data.split('|')[1])


@bot.callback_query_handler(func=lambda call: call.data.startswith("repair_vehicle"))
def charge(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    controller.insert(Serve.Serve(call.from_user.id, call.data.split('|')[1]))
    bot.send_message(call.message.chat.id,
                     "Great job! You repaired scooter with id = " + call.data.split('|')[1],
                     reply_markup=ReplyKeyboardRemove())
    controller.repair_vehicle()


@bot.callback_query_handler(func=lambda call: call.data.startswith("end_rent"))
def send_scooter_location(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    latitude = float(call.data.split('|')[1])
    longitude = float(call.data.split('|')[2])
    end_ride_handler(latitude, longitude, int(call.data.split('|')[3]), float(call.data.split('|')[4]))
    reply = "Ride ended 🏁"
    if len(call.data.split('|')) == 6:
        current_user.bonus_points -= int(float(call.data.split('|')[4]))
        reply += "\nYou have spent " + str(int(float(call.data.split('|')[4]))) + " bonuses, " + str(
            int(float(current_user.bonus_points))) + " left"
        controller.update_bonuses(current_user)

    bot.send_message(call.message.chat.id, reply, reply_markup=ReplyKeyboardRemove())


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


@bot.message_handler(content_types="text")
def default(message):
    if len(controller.user_exists(message.from_user.id)) > 0:
        user = controller.user_exists(message.from_user.id)[0]
        global current_user
        if current_user.identifier is None:
            current_user = User.User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])
            current_user.cards = []
            for card in controller.get_cards(current_user):
                current_user.cards.append(Card.Card(card[1], card[2]))
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("Nearest scooters 🗺️", callback_data="nearest_scooters"))
        if current_user.currently_used_vehicle is None:
            keyboard.row().add(
                telebot.types.InlineKeyboardButton("Start a ride 🛴", callback_data="rent_scooter"))
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("All my rides 🗒️", callback_data="all_rides"))
        keyboard.row().add(
            telebot.types.InlineKeyboardButton("Total spent 💵", callback_data="all_expenses"))
        bot.send_message(message.chat.id, text="Menu 📌", reply_markup=keyboard)
    elif len(controller.employee_exists(message.from_user.id)) > 0:
        employee = controller.employee_exists(message.from_user.id)
        employee = employee[0]
        global current_employee
        current_employee = Employee.Employee(employee[0], employee[1])
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Statistic 📝",
                                               callback_data="statistic")
        )
        if current_employee.specialization is False:
            keyboard.row(
                telebot.types.InlineKeyboardButton("Charge ⚡",
                                                   callback_data="nearest_scooters")
            )
        else:
            keyboard.row(
                telebot.types.InlineKeyboardButton("Repair 🛠️",
                                                   callback_data="nearest_scooters")
            )
        bot.send_message(message.chat.id, text="Menu 📌", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Please register first 🔑")


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
    else:
        state = rent_handler(message.text)
        if state == 0:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(telebot.types.InlineKeyboardButton("End ride 🏁", callback_data="end_ride"))
            bot.send_message(message.chat.id, "Use the button below to end the ride ⬇", reply_markup=keyboard)
        if state == 1:
            bot.send_message(message.chat.id, "It seems the scooter is already in use.\nPlease choose another one")
        elif state == 2:
            bot.send_message(message.chat.id, "It seems the scooter is broken or damaged.\nPlease choose another one")
        elif state == 3:
            bot.send_message(message.chat.id,
                             "Scooter with the code specified is not found.\nPlease check the code and try again")


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


def radius_handler(message):
    try:
        str1 = "Employees:"
        if len(controller.get_employee_by_zone_radius(int(message.text))) == 0:
            message = bot.send_message(message.chat.id, "There no such employees")
        else:
            for row in controller.get_employee_by_zone_radius(int(message.text)):
                if str(row[1]):
                    spec = "repairer"
                else:
                    spec = "charger"
                str1 = str1 + "\nEmployee id: " + str(row[0]) + ", employee specialization: " + spec

            message = bot.send_message(message.chat.id, str1)
            bot.register_next_step_handler(message, default)
    except ValueError:
        message = bot.send_message(message.chat.id, "Wrong input, please try again")
        bot.register_next_step_handler(message, radius_handler)


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

        vehicles = None

        if current_user.identifier is not None:
            vehicles = controller.get_all_vehicles_for_user()
        elif current_employee.identifier is not None:
            if current_employee.specialization is False:
                vehicles = controller.get_all_vehicles_for_charger()
            elif current_employee.specialization is True:
                vehicles = controller.get_all_vehicles_for_repairer()

        for vehicle in vehicles:
            vehicle = Vehicle.Vehicle(vehicle[0], vehicle[1], vehicle[2], vehicle[3], vehicle[4], vehicle[5],
                                      vehicle[6], vehicle[7], vehicle[8])
            scooters.append([round(geodesic((latitude, longitude), (vehicle.latitude, vehicle.longitude)).meters),
                             vehicle])

        scooters.sort(key=get_first)

        del scooters[3:]

        for scooter in scooters:
            scooter = scooter[1]
            text = ""
            if current_user.identifier is not None:
                text = "🛴 🗺️ " + str(
                    round(
                        geodesic((latitude, longitude), (scooter.latitude, scooter.longitude)).meters)) + "m 🔋 " + str(
                    scooter.charge_level) + "% " + str(scooter.cents_per_minute) + "¢/min"
            elif current_employee.identifier is not None:
                if current_employee.specialization is False:
                    text = "🛴 🗺️ " + str(
                        round(
                            geodesic((latitude, longitude),
                                     (scooter.latitude, scooter.longitude)).meters)) + "m 🔋 " + str(
                        scooter.charge_level) + "%"
                elif current_employee.specialization is True:
                    text = "🛴 🗺️ " + str(
                        round(
                            geodesic((latitude, longitude),
                                     (scooter.latitude, scooter.longitude)).meters)) + "m 🔋 " + str(
                        scooter.charge_level) + "% 🩹 Broken or damaged"
            keyboard.row().add(
                telebot.types.InlineKeyboardButton(text, callback_data="send_scooter_location|" + str(
                    scooter.latitude) + "|" + str(
                    scooter.longitude) + "|" + str(scooter.identifier)))
        bot.send_message(message.chat.id, "Nearest scooters", reply_markup=keyboard)
    except AttributeError:
        bot.send_message(message.chat.id, "Wrong input, try again ❌")
        bot.register_next_step_handler(message, current_user_location)


def current_user_location_ride_end(message):
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude

        zone_id = None
        for zone in controller.get_all("allowed_zone"):
            if round(geodesic((latitude, longitude), (zone[1], zone[2])).meters) < zone[3]:
                zone_id = zone[0]
                break

        if zone_id is None:
            bot.send_message(message.chat.id,
                             "You are out of allowed zone, please enter the allowed zone and try again")
            bot.register_next_step_handler(message, current_user_location_ride_end)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            duration = (datetime.now() - controller.get_ride(current_user, current_user.currently_used_vehicle)[0][
                1]).total_seconds() // 60
            current_user.bonus_points += duration // 5
            price = 1 + duration // 60 * current_user.currently_used_vehicle.cents_per_minute / 100
            for card in current_user.cards:
                keyboard.row().add(
                    telebot.types.InlineKeyboardButton(card.name,
                                                       callback_data="end_rent|" + str(latitude) + "|" + str(
                                                           longitude) + "|" + str(zone_id) + "|" + str(price)))
            if current_user.bonus_points >= round(price):
                keyboard.row().add(
                    telebot.types.InlineKeyboardButton("Pay with bonuses 🤑",
                                                       callback_data="end_rent|" + str(latitude) + "|" + str(
                                                           longitude) + "|" + str(zone_id) + "|" + str(
                                                           price) + "|" + "bonuses_payment"))
            message = bot.send_message(message.chat.id, "Ride price: " + str(price) + "$\nChoose payment method 💳",
                                       reply_markup=keyboard)
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
