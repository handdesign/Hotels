from loader import bot, data_common
from telebot import types
from utils.utils import city_choice


@bot.message_handler(commands=['lowprice'])
def low(message):
    """
    Функция реагирует на команду /lowprice. Определяет метод сортировки показа отелей.
    Присваивает словарю data_common метод сортировки, ключом является id пользователя.

    :param message: команда пользователя
    btn_remove: удаляет клавиатуру из кнопок
    sorting: определяет метод сортировки отелей
    :return: None
    """
    btn_remove = types.ReplyKeyboardRemove()
    sorting = 'PRICE_LOW_TO_HIGH'
    bot.send_message(
        chat_id=message.chat.id,
        text='Введите город, в котором нужно искать отели',
        reply_markup=btn_remove
    )
    data_common[message.from_user.id] = [sorting]
    bot.register_next_step_handler(message, city_choice)
