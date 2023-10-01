import telebot
from requests_to_API.cur import currency_converter
from dotenv import load_dotenv
import os


load_dotenv()
api_token = os.getenv("API_TOKEN")
bot = telebot.TeleBot(api_token)

LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

data_quest = (
    'Введите минимальную стоимость одной ночи в рублях',
    'Введите максимальную стоимость одной ночи в рублях',
    'Введите максимальное расстояние от центра в километрах'
)

data_common = dict()
data_history = dict()

currency_now = currency_converter()
