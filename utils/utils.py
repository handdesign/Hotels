from loader import bot, data_common, data_history, data_quest, LSTEP, currency_now
from telebot import types
from urllib.request import urlopen
from requests_to_API.find_city import find_cities
from utils.translate import TranslateCity
from requests_to_API.get_hotels import input_data
from requests_to_API.hotel_detail import property_hotel
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import datetime


def city_choice(message):
    """
    Функция принимает сообщение от пользователя с названием города и предоставляет
    пользователю выбор из найденных городов.

    :param message: название города
    city: переводит текст пользователя на английский язык
    markup: создает клавиатуру из кнопок
    buttons_added: список найденных городов
    found: экземпляр класса find_cities() для поиска городов

    :return: None
    """
    city = TranslateCity.translate_city(message.text)
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons_added = list()
    found = find_cities(city)
    for item in found:
        buttons_added.append(types.InlineKeyboardButton(text=item,
                                                        callback_data=found[item]))
    if not buttons_added:
        bot.send_message(message.chat.id, 'Ничего не найдено, попробуйте еще раз')
        bot.register_next_step_handler(message, city_choice)
    else:
        markup.add(*buttons_added)
        bot.send_message(message.from_user.id, 'Выберете город из списка:', reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: (call.data not in ['Да', 'Нет']) and (call.data.startswith('cbcal') != True))
def quantity_hotels(call):
    """
    Функция принимает id города и добавляет его в словарь data_common.
    Отправляет пользователю вопрос.

    :param call: id города

    :return: None
    """
    if call.data:
        data_common[call.from_user.id].append(call.data)
        bot.send_message(call.message.chat.id, 'Сколько отелей показать?')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=None
                                      )
        if 'DISTANCE' in data_common[call.from_user.id]:
            bot.register_next_step_handler(call.message, dist_quest)
        else:
            bot.register_next_step_handler(call.message, calendar_in)


def dist_quest(message):
    """
    Функция принимает кол-во отелей и добавляет в словарь data_common.
    Перебирает кортеж data_quest и добавляет значение параметра message в словарь data_common.

    :param message: кол-во отелей и ответы на вопросы из кортежа data_common.

    :return: None
    """
    try:
        if int(message.text) > 0:
            data_common[message.from_user.id].append(message.text)
            if len(data_common[message.from_user.id]) == 5:
                bot.send_message(chat_id=message.chat.id, text=f'{data_quest[2]}')
                bot.register_next_step_handler(message, calendar_in)
            else:
                quest_id = len(data_common[message.from_user.id]) - 3
                bot.send_message(chat_id=message.chat.id, text=f'{data_quest[quest_id]}')
                bot.register_next_step_handler(message, dist_quest)
                return
        else:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=f'Ожидается положительное целое число.\n Попробуйте еще раз.')
        bot.register_next_step_handler(message, dist_quest)


def calendar_in(message):
    """
    Функция принимает значение из ответа пользователя и добавляет в словарь data_common.
    Создает календарь для выбора даты заезда.

    :param message: ответ на вопрос

    :return: None
    """
    data_common[message.from_user.id].append(message.text)
    bot.send_message(message.chat.id, f'Выберите дату заезда')
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
    bot.send_message(message.chat.id,
                     f"Выберете {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_out(message):
    """
    Функция принимает дату заезда.
    Создает календарь для выбора даты выезда.

    :param message: дата заезда

    :return: None
    """
    bot.send_message(message.chat.id, f'Выберите дату выезда')
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
    bot.send_message(message.chat.id,
                     f"Выберете {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal_in(call):
    """
    Функция принимает календарь заезда.
    Редактирует календарь.

    :param call: календарь заезда

    :return: None
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        data_common[call.from_user.id].append(result.isoformat().split('-'))
        calendar_out(call.message)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal_out(call):
    """
    Функция принимает календарь выезда.
    Редактирует календарь.

    :param call: календарь выезда

    :return: None
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        data_common[call.from_user.id].append(result.isoformat().split('-'))
        questions(call)


def questions(message):
    """
    Функция принимает дату выезда.
    Создает клавиатуру для показа фотографий.

    :param message: дата выезда
    markup: создает клавиатуру из кнопок
    btn_yes, btn_no: кнопки

    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_yes = types.InlineKeyboardButton(text='Да', callback_data='Да')
    btn_no = types.InlineKeyboardButton(text='Нет', callback_data='Нет')
    markup.add(btn_yes, btn_no)
    bot.send_message(message.from_user.id, text='Показать фотографии?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Да', 'Нет'])
def photo_answer(call):
    """
    Функция принимает ответ пользователя.
    Отправляет найденные отели пользователю либо передает их следующей функции.
    Добавляет найденные отели в словарь  data_history.

    :param call: ответ пользователя
    minus: значение для вычета, зависит от сортировки отелей
    d_taken: значение словаря data_common
    sorting: сортировка отелей
    city_id: id города
    quantity: кол-во отелей
    date_in: дата заезда
    date_out: дата выезда
    d_in: словарь даты заезда
    d_out: словарь даты выезда
    search: экземпляр класса input_data()
    prop: экземпляр класса property_hotel()
    text: список с описанием отеля
    date_now: фиксирует время отправки отеля

    :return: None
    """
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=None
                                  )
    data_common[call.from_user.id].append(call.data)
    if 'DISTANCE' in data_common[call.from_user.id]:
        minus = 0
    else:
        minus = 3
    d_taken = data_common[call.from_user.id]
    sorting, city_id, quantity = d_taken[0], d_taken[1], int(d_taken[2])

    date_in = d_taken[6 - minus]
    date_out = d_taken[7 - minus]

    d_in = dict()
    d_in["day"], d_in["month"], d_in["year"] = int(date_in[2]), int(date_in[1]), int(date_in[0])
    d_out = dict()
    d_out["day"], d_out["month"], d_out["year"] = int(date_out[2]), int(date_out[1]), int(date_out[0])

    if sorting == 'DISTANCE':
        search = input_data(
            city_request=city_id,
            date_in=d_in,
            date_out=d_out,
            quantity=quantity,
            sort_property=sorting,
            max_price=round(int(d_taken[4]) * currency_now),
            min_price=round(int(d_taken[3]) * currency_now)
        )
    elif sorting == 'PRICE_HIGH_TO_LOW':
        search_hotels = input_data(
            city_request=city_id,
            date_in=d_in,
            date_out=d_out,
            quantity=200,
            sort_property='PRICE_LOW_TO_HIGH',
            min_price=400
        )
        sorted_hotels = sorted(search_hotels, key=search_hotels.get, reverse=True)
        search_id = sorted_hotels[: quantity]
        search = dict()
        for item in search_id:
            search[item] = search_hotels[item]
    else:
        search = input_data(
            city_request=city_id,
            date_in=d_in,
            date_out=d_out,
            quantity=quantity,
            sort_property=sorting
        )

    if 'Нет' in d_taken:
        for hotel in search:
            prop = property_hotel(hotel)
            name, description, address, price, destin = prop[0], prop[1], prop[2], search[hotel][1], search[hotel][2]

            text = [name, description, address, price, destin]
            bot.send_message(chat_id=call.message.chat.id, text=''.join(text))

            date_now = datetime.now().strftime('%d.%m.%y %H:%M:%S')
            history_key = ' '.join([str(call.from_user.id), date_now])
            data_history[history_key] = [sorting, date_now, name, description, address, price, destin]

    elif 'Да' in d_taken:
        data_common[call.from_user.id].append(search)
        bot.send_message(call.message.chat.id, 'Сколько фото показать?')
        bot.register_next_step_handler(call.message, photo_quantity)


def photo_quantity(message):
    """
    Функция принимает кол-во фото.
    Отправляет найденные отели пользователю либо передает их следующей функции.
    Добавляет найденные отели в словарь  data_history.

    :param message: кол-во фото
    search: информация об отеле
    prop: экземпляр класса property_hotel()
    text: список с описанием отеля
    photo_list: список ссылок на фото отеля
    media_group: список медиаданных для группировки фото
    date_now: фиксирует время отправки отеля

    :return: None
    """
    search = data_common[message.from_user.id][-1]
    for hotel in search:
        prop = property_hotel(hotel)
        name, description, address, price, destin = prop[0], prop[1], prop[2], search[hotel][1], search[hotel][2]

        text = [name, description, address, price, destin]
        bot.send_message(chat_id=message.chat.id, text=''.join(text))

        photo_list = prop[3]
        media_group = list()

        max_photo = int(message.text)
        count = 0
        for item in photo_list:
            count += 1
            if count > max_photo:
                break
            media_group.append(types.InputMediaPhoto(urlopen(item)))
        bot.send_media_group(chat_id=message.chat.id, media=media_group)

        date_now = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        hist_key = ' '.join([str(message.from_user.id), date_now])
        sorting = data_common[message.from_user.id][0]
        data_history[hist_key] = [sorting, date_now, name, description, address, price, destin, max_photo, photo_list]