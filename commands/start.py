from loader import bot
from telebot import types


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    Функция реагирует на команду /start. Приветствует пользователя.
    Создает кнопки для быстрого выбора вариантов.
    Отправляет команду, при нажатии на кнопку.

    :param message: команда пользователя
    markup: создает клавиатуру из кнопок
    btn_lowprice, btn_highprice, btn_bestdeal, btn_history: создают кнопки
    welcome: приветственное сообщение
    :return: None
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_lowprice = types.KeyboardButton('/lowprice')
    btn_highprice = types.KeyboardButton('/highprice')
    btn_bestdeal = types.KeyboardButton('/bestdeal')
    btn_history = types.KeyboardButton('/history')
    markup.add(btn_lowprice, btn_highprice)
    markup.add(btn_bestdeal, btn_history)

    welcome = 'Привет! Я найду для тебя отели в любом городе на сайте hotels.com\nДля начала выбери параметр поиска.'
    bot.send_message(chat_id=message.chat.id, text=welcome, reply_markup=markup)
