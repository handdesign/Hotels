import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_token = os.getenv("X-RapidAPI-Key")


def currency_converter():
    url = "https://twelve-data1.p.rapidapi.com/currency_conversion"

    querystring = {"symbol": "RUB/USD", "amount": "1"}

    headers = {
        "X-RapidAPI-Key": api_token,
        "X-RapidAPI-Host": "twelve-data1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    price = json.loads(response.text)['rate']

    return price
