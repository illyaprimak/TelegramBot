import telebot

bot = telebot.TeleBot('1198725614:AAECjKvTD7fpK_rO21vxsBpNYwKgJJluxC8')
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Привет', 'Пока')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Доброго дня, козаче! Я бот що здає в аренду електросамокати та велосипеди. Якщо хочешь щось від мене, то натискай на кнопки))0)0)', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Категорично вас вітаю!')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Допобачення')
    elif message.text.lower() == 'я тебя люблю':
        bot.send_location(message.chat.id, 49.33273504,17.61087799)

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)

bot.polling()