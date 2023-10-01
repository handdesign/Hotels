from urllib.request import urlopen
from loader import bot, data_history
from telebot import types


@bot.message_handler(commands=['history'])
def hist(message):
    """
    Функция реагирует на команду /history. Отправляет пользователю список отелей из
    словаря data_history. Где ключом является id пользователя и время отправки информации
    об отеле пользователю.

    :param message: команда пользователя
    d_taken: список информации об отеле
    name: название отеля
    description: описание отеля
    address: адрес отеля
    price: цена за одну ночь
    destin: расстояние от отеля до центра города
    text: список с информацией об отеле, который отправляется пользователю
    photo_list: список ссылок на фото отеля, если в d_taken есть вложенный список на последней позиции
    media_group: список медиаданных для отправки пользователю сгруппированные фото отеля
    max_photo: максимальное кол-во фото для отправки пользователю

    :return: None
    """
    for item in data_history.keys():
        if str(item).startswith(str(message.from_user.id)):
            d_taken = data_history[item]
            name, description, address, price, destin = d_taken[2], d_taken[3], d_taken[4], d_taken[5], d_taken[6]
            text = [name, description, address, price, destin]

            if d_taken[0] == 'PRICE_LOW_TO_HIGH':
                sorting = '/lowprice'
            elif d_taken[0] == 'PRICE_HIGH_TO_LOW':
                sorting = '/highprice'
            else:
                sorting = '/bestdeal'

            bot.send_message(chat_id=message.chat.id, text=sorting)
            bot.send_message(chat_id=message.chat.id, text=d_taken[1])
            bot.send_message(chat_id=message.chat.id, text=''.join(text))
            if isinstance(d_taken[-1], list):
                photo_list = d_taken[-1]
                media_group = list()
                max_photo = d_taken[-2]
                count = 0
                for item_data in photo_list:
                    count += 1
                    if count > max_photo:
                        break
                    media_group.append(types.InputMediaPhoto(urlopen(item_data)))
                bot.send_media_group(chat_id=message.chat.id, media=media_group)
