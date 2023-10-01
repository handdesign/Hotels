import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_token = os.getenv("X-RapidAPI-Key")


def find_cities(city):
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": city, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": api_token,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    destinations = json.loads(response.text)

    cities_dict = dict()
    for item in destinations['sr']:
        if item['type'] == 'CITY':
            cities_dict[item['regionNames']['displayName']] = item['gaiaId']

    return cities_dict
